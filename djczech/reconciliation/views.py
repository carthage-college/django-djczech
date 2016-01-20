from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

from djczech.reconciliation.data.models import Cheque
from djczech.reconciliation.forms import ChequeDataForm
from djczech.reconciliation.utils import handle_uploaded_file, recce_cheques

from djtools.decorators.auth import group_required, portal_auth_required

from sqlalchemy import exc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datatables import DataTable
from datetime import datetime
from itertools import islice

import os
import csv

EARL = settings.INFORMIX_EARL


#@portal_auth_required("BusinessOfficeAdmin", reverse_lazy("access_denied"))
#@group_required()
@staff_member_required
def cheque_data(request):
    """
    Form that allows the user to upload bank data in CSV format
    and then inserts the data into the database
    """

    # lists for recording results
    data = None
    cheques = []
    fail = []
    uid = request.GET.get("uid")
    if request.method=='POST':
        form = ChequeDataForm(request.POST, request.FILES)
        if form.is_valid():
            # database connection
            engine = create_engine(EARL)
            Session = sessionmaker(bind=engine)
            session = Session()
            session.autoflush = False
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
            reader = csv.DictReader(f, fieldnames, delimiter=',')

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

            # commit the reconciliation updates
            #session.commit()

            rsvp = render_to_response(
                "reconciliation/data_form.html", {
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
        "reconciliation/data_form.html", {
            "form":form,"earl":EARL,"uid":uid
        },
        context_instance=RequestContext(request)
    )

