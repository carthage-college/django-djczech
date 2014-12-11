from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required

from djczech.reconciliation.data.models import Cheque
from djczech.reconciliation.forms import ChequeDataForm

from djzbar.utils.informix import do_sql as do_esql
from djzbar.settings import INFORMIX_EARL

from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import text

import csv


@staff_member_required
def cheque_data(request):
    """
    Form that allows the user to upload bank data in CSV format
    and then inserts the data into the database
    """
    if request.method=='POST':
        form = ChequeDataForm(request.POST, request.FILES)
        if form.is_valid():
            # database connection
            engine = create_engine(INFORMIX_EARL)
            Session = sessionmaker(bind=engine)
            session = Session()
            # remove old objects for now
            session.query(Cheque).delete()
            session.commit()
            # munge the data from CSV file
            bank_data = form.cleaned_data['bank_data']
            fieldnames = (
                "jbaccount","jbchkno","jbaction","jbamount","jbissue_date",
                "jbpostd_dat","jbstatus","jbstatus_date","jbpayee"
            )
            reader = csv.DictReader(bank_data, fieldnames)
            seq = 1
            fmt = "%m/%d/%Y"
            for r in reader:
                try:
                    jbissue_date = datetime.strptime(r["jbissue_date"], fmt)
                except:
                    jbissue_date = ""

                try:
                    jbstatus_date = datetime.strptime(r["jbstatus_date"], fmt)
                except:
                    jbstatus_date = ""

                try:
                    jbamount = float(r["jbamount"][1:])
                except:
                    jbamount = 0

                jbaction = r["jbaction"]
                if r["jbstatus"] == "Stale" or r["jbstatus"] == "Void":
                    jbaction = "X"

                cheque = Cheque(
                    jbchkno=r["jbchkno"],
                    jbstatus_date=jbstatus_date, jbstatus=r["jbstatus"],
                    jbaction=jbaction, jbaccount=r["jbaccount"],
                    jbamount=jbamount, jbissue_date=jbissue_date,
                    jbpostd_dat=r["jbpostd_dat"], jbpayee=r["jbpayee"],
                    jbseqno=seq
                )
                seq += 1

                # insert the data
                session.add(cheque)

            session.commit()
            session.close()

            return HttpResponseRedirect(
                reverse("cheque_data_success")
            )
    else:
        form = ChequeDataForm()
    return render_to_response(
        "reconciliation/cheque/data_form.html",
        {"form": form,},
        context_instance=RequestContext(request)
    )


@staff_member_required
def cheque_list(request):
    # database connection
    engine = create_engine(INFORMIX_EARL)
    Session = sessionmaker(bind=engine)
    session = Session()
    # query
    cheques = session.query(Cheque).all()
    session.close()

    return render_to_response(
        "dashboard/cheque/list.html",
        {"cheques": cheques,},
        context_instance=RequestContext(request)
    )


@staff_member_required
def cheque_detail(request, cid=None):
    if not cid:
        # search POST
        try:
            cid = request.POST["cid"]
        except:
            return HttpResponseRedirect(
                reverse("cheque_list")
            )

    # database connection
    engine = create_engine(INFORMIX_EARL)
    Session = sessionmaker(bind=engine)
    session = Session()
    cheque = session.query(Cheque).get(cid)
    session.close()

    return render_to_response(
        "dashboard/cheque/search.html",
        {"cheque":cheque,},
        context_instance=RequestContext(request)
    )

