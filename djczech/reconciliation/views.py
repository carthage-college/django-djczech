from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404

from djczech.reconciliation.forms import ChequeDataForm
from djtools.utils.mail import send_mail
from djzbar.utils.informix import do_sql as do_esql

import csv

def cheque_data(request):
    """
    Form that allows the user to upload bank data in CSV format
    and then inserts the data into the database
    """
    if request.method=='POST':
        form = ChequeDataForm(request.POST, request.FILES)
        if form.is_valid():
            bank_data = form.cleaned_data['bank_data']

            # munge the data
            fieldnames = (
                "jbimprt_date", "jbchkno", "jbstatus_date", "jbstatus",
                "jbaction", "jbaccount", "jbamount", "jbissue_date",
                "jbpostd_dat", "jbpayee", "jbseqno"
            )
            reader = csv.DictReader( bank_data, fieldnames )
            jason = json.dumps( [ row for row in reader ] )

            # insert the data
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
            *
        FROM
            ccreconjb_rec
        ORDER_BY
            jbissue_date
    """
    cheques = do_esql(sql)
    return render_to_response(
        "reconciliation/cheque/list.html",
        {"cheques": cheques,},
        context_instance=RequestContext(request)
    )


def cheque_search(request):
    return render_to_response(
        "reconciliation/cheque/search.html",
        context_instance=RequestContext(request)
    )

