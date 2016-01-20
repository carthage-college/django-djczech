from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from djczech.reconciliation.data.models import Cheque

from djtools.decorators.auth import group_required, portal_auth_required

from sqlalchemy import desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datatables import DataTable
from itertools import islice

import os
import csv


import logging
logger = logging.getLogger(__name__)

EARL = settings.INFORMIX_EARL

#@group_required()
@staff_member_required
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
        "search.html",
        {"cheque":cheque,},
        context_instance=RequestContext(request)
    )


#@group_required()
#@staff_member_required
def cheque_ajax(request):
    # database connection
    engine = create_engine(EARL)
    Session = sessionmaker(bind=engine)
    session = Session()
    # query
    #cheques = session.query(Cheque).order_by(desc(jbissue_date)).limit(length)
    #cheques = session.query(Cheque).order_by(desc(Cheque.jbissue_date))
    #cheques = session.query(Cheque)
    cheques = session.query(Cheque).filter_by(jbstatus="I")
    # datatable
    table = DataTable(request.GET, Cheque, cheques, [
        "jbchkno",
        "jbchknolnk",
        "jbstatus",
        "jbstatus_date",
        "jbimprt_date",
        "jbaccount",
        "jbamount",
        "jbamountlnk",
        "jbpayee"
    ])

    table.add_data(link=lambda o: reverse_lazy("cheque_detail", args=[o.jbchkno]))
    table.add_data(pk=lambda o: o.jbchkno)
    #table.searchable(lambda queryset, user_input: cheque_search(queryset, user_input))
    session.close()
    logger.debug("table.json() = {}".format(table.json()))
    return JsonResponse(table.json(), safe=False)
    #return HttpResponse(table.json(), content_type='application/json')

#@group_required()
@staff_member_required
def cheque_list(request):
    # database connection
    engine = create_engine(EARL)
    Session = sessionmaker(bind=engine)
    session = Session()
    # query
    #cheques = session.query(Cheque).filter_by(jbstatus=settings.AUTO_REC)
    #cheques = session.query(Cheque).filter_by(jbstatus=settings.IMPORT_STATUS)
    cheques = session.query(Cheque).filter_by(jbstatus="I")
    #.order_by(desc(jbissue_date))
    #.limit(100)
    session.close()

    return render_to_response(
        "list.html",
        {"objs": cheques},
        context_instance=RequestContext(request)
    )
