from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from djczech.reconciliation.data.models import Cheque
from djczech.reconciliation.forms import ChequeDataForm
from djczech.reconciliation.utils import handle_uploaded_file, recce_cheques

from djtools.utils.users import in_group
from djtools.decorators.auth import portal_auth_required

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import desc
from datatables import DataTable
from datetime import date, datetime
from itertools import islice

import os
import csv

EARL = settings.INFORMIX_EARL

@portal_auth_required(reverse_lazy("access_denied"))
def cheque_data(request):
    """
    Form that allows the user to upload bank data in CSV format
    and then inserts the data into the database
    """

    # lists for recording results
    data = None
    cheques = []
    fail = []
    if request.method=='POST':
        form = ChequeDataForm(request.POST, request.FILES)
        if form.is_valid():
            # database connection
            engine = create_engine(EARL)
            Session = sessionmaker(bind=engine)
            session = Session()
            # convert date to datetime
            import_date = datetime.combine(
                form.cleaned_data['import_date'], datetime.min.time()
            )
            # for some reason we set jbpayee equal to the import date
            # plus user info
            jbpayee = "{}_{}".format(
                form.cleaned_data['import_date'], "business_office"
            )
            # CSV headers
            fieldnames = (
                "jbstatus_date", "jbstatus", "jbamount",
                "jbaccount", "jbchkno", "jbpayee"
            )
            # obtain the CSV file from POST and upload
            phile = handle_uploaded_file(request.FILES['bank_data'])
            # remove all lines up to and including the headers line
            with open(phile, "r") as f:
                n = 0
                for line in f.readlines():
                    n += 1
                    # line in which field headers live
                    if 'As of date' in line:
                        break
                f.close()
                f = islice(open(phile, "r"), n, None)

            # read the CSV file
            reader = csv.DictReader(f, fieldnames, delimiter='\t')

            # for each line create a Cheque object
            for r in reader:
                # convert amount from string to float and strip dollar sign
                try:
                    jbamount = float(r["jbamount"][1:].replace(',',''))
                except:
                    jbamount = 0
                # status date
                try:
                    jbstatus_date = datetime.strptime(
                        r["jbstatus_date"], "%m/%d/%Y"
                    )
                except:
                    jbstatus_date = None
                # check number
                try:
                    cheque_number = int(r["jbchkno"])
                except:
                    cheque_number = 0

                # create a Cheque object
                cheque = Cheque(
                    jbimprt_date=import_date,
                    jbstatus_date=jbstatus_date,
                    jbchkno=cheque_number, jbchknolnk=cheque_number,
                    jbstatus=settings.IMPORT_STATUS, jbaction="",
                    jbaccount=r["jbaccount"], jbamount=jbamount,
                    jbamountlnk=jbamount, jbpayee=jbpayee
                )

                try:
                    # insert the data
                    session.add(cheque)
                    session.flush()
                    cheques.append(cheque.__dict__)
                except exc.SQLAlchemyError as e:
                    fail.append(cheque.__dict__)
                    session.rollback()
            # execute the reconciliation process
            data = recce_cheques(request, session, import_date)

            session.commit()

            rsvp = render_to_response(
                "reconciliation/cheque/data_form.html", {
                    "form":form, "earl":EARL, "fail":fail,
                    "cheques":cheques, "data":data
                },
                context_instance=RequestContext(request)
            )
            # done
            session.close()
            return rsvp
    else:
        form = ChequeDataForm()
    return render_to_response(
        "reconciliation/cheque/data_form.html", {
            "form":form,"earl":EARL
        },
        context_instance=RequestContext(request)
    )

def cheque_detail(request, cid=None):
    if not cid:
        # search POST
        try:
            cid = request.POST["cid"]
        except:
            return HttpResponseRedirect(
                reverse_lazy("cheque_list")
            )

    # database connection
    engine = create_engine(EARL)
    Session = sessionmaker(bind=engine)
    session = Session()
    cheque = session.query(Cheque).get(cid)
    session.close()

    return render_to_response(
        "dashboard/cheque/search.html",
        {"cheque":cheque,},
        context_instance=RequestContext(request)
    )


def cheque_ajax(request):
    # database connection
    engine = create_engine(EARL)
    Session = sessionmaker(bind=engine)
    session = Session()
    # query
    #cheques = session.query(Cheque).order_by(desc(jbissue_date)).limit(length)
    #cheques = session.query(Cheque).order_by(desc(Cheque.jbissue_date))
    cheques = session.query(Cheque)
    # datatable
    table = DataTable(request.GET, Cheque, cheques, [
        "jbchkno",
        "jbimprt_date",
        "jbstatus",
        "jbstatus_date",
        "jbaction",
        "jbaccount",
        "jbamount",
        "jbissue_date",
        "jbpostd_dat",
        "jbpayee",
        "jbseqno"
    ])

    table.add_data(link=lambda o: reverse_lazy("cheque_detail", args=[o.jbchkno]))
    table.add_data(pk=lambda o: o.jbchkno)
    #table.searchable(lambda queryset, user_input: cheque_search(queryset, user_input))

    session.close()
    return JsonResponse(table.json())

def cheque_list(request):
    # database connection
    engine = create_engine(EARL)
    Session = sessionmaker(bind=engine)
    session = Session()
    # query
    cheques = session.query(Cheque).filter_by(jbstatus=settings.IMPORT_STATUS)
    #.order_by(desc(jbissue_date))
    #.limit(100)
    session.close()

    return render_to_response(
        "dashboard/cheque/list.html",
        {"cheques": cheques},
        context_instance=RequestContext(request)
    )
