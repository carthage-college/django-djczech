from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from djczech.reconciliation.data.models import Cheque
from djczech.reconciliation.forms import ChequeDataForm

from djzbar.utils.informix import do_sql as do_esql
from djzbar.settings import INFORMIX_EARL

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import text

import csv


def cheque_data(request):
    """
    Form that allows the user to upload bank data in CSV format
    and then inserts the data into the database
    """
    if request.method=='POST':
        form = ChequeDataForm(request.POST, request.FILES)
        if form.is_valid():
            # the CSV file
            bank_data = form.cleaned_data['bank_data']
            # database connection
            engine = create_engine(INFORMIX_EARL_PROD)
            Session = sessionmaker(bind=engine)
            session = Session()
            # munge the data
            fieldnames = (
                "jbaccount","jbchkno","Null","jbamount","jbissue_date",
                "jbpostd_dat","jbstatus","jbstatus_date","jbpayee"
            )
            reader = csv.DictReader(bank_data, fieldnames)
            for r in reader:
                cheque = Cheque(
                    jbchkno=r["jbchkno"],
                    jbstatus_date=r["jbstatus_date"], jbstatus=r["jbstatus"],
                    jbaction=r["jbaction"], jbaccount=r["jbaccount"],
                    jbamount=r["jbamount"], jbissue_date=r["jbissue_date"],
                    jbpostd_dat=r["jbpostd_dat"], jbpayee=r["jbpayee"],
                    jbseqno=r["jbseqno"]
                )

                # insert the data
                session.add(cheque)

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


def cheque_list(request):
    sql = """
        SELECT
            first 1000
            *
        FROM
            ccreconjb_rec
        ORDER BY
            jbissue_date
    """
    cheques = do_esql(
        sql, key=settings.INFORMIX_DEBUG, earl=settings.INFORMIX_EARL
    )
    return render_to_response(
        "dashboard/cheque/list.html",
        {"cheques": cheques,},
        context_instance=RequestContext(request)
    )


def cheque_search(request):
    return render_to_response(
        "reconciliation/cheque/search.html",
        context_instance=RequestContext(request)
    )

