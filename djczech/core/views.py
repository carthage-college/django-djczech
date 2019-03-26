from django.conf import settings
from django.template import RequestContext
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from djczech.reconciliation.data.models import Cheque
from djzbar.decorators.auth import portal_auth_required

from sqlalchemy import desc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datatables import DataTable

import os

EARL = settings.INFORMIX_EARL


@portal_auth_required(
    'BusinessOfficeFinance',
    'BusinessOfficeFinance', reverse_lazy('access_denied')
)
def cheque_detail(request, sid=None):

    # database connection
    engine = create_engine(EARL)
    Session = sessionmaker(bind=engine)
    session = Session()
    cheque = session.query(Cheque).filter_by(jbseqno=sid).one()
    session.close()

    return render(request, 'search.html', {'cheque':cheque,})


@portal_auth_required(
    'BusinessOfficeFinance',
    'BusinessOfficeFinance', reverse_lazy('access_denied')
)
def cheque_ajax(request):
    # database connection
    engine = create_engine(EARL)
    Session = sessionmaker(bind=engine)
    session = Session()
    # query
    #cheques = session.query(Cheque).order_by(desc(jbissue_date)).limit(length)
    #cheques = session.query(Cheque).order_by(desc(Cheque.jbissue_date))
    # datatable
    recci = request.GET
    status = 'I'
    if request.POST:
        status = request.POST.get('status')
        recci = request.POST
    cheques = session.query(Cheque).filter_by(jbstatus=status)
    table = DataTable(recci, Cheque, cheques, [
        'jbseqno',
        'jbchkno',
        'jbchknolnk',
        'jbstatus',
        'jbstatus_date',
        'jbimprt_date',
        'jbaccount',
        'jbamount',
        'jbamountlnk',
        'jbpayee'
    ])

    if not recci:
        return JsonResponse(
            {'message':"Missing GET/POST data for 'status' field"}, safe=False
        )
    else:
        table.add_data(link=lambda o: reverse_lazy('cheque_detail', args=[o.jbchkno]))
        table.add_data(pk=lambda o: o.jbchkno)
        #table.searchable(lambda queryset, user_input: cheque_search(queryset, user_input))
        session.close()
        jason = table.json()
        # DT_RowData dictionary contains a key named 'link', which is
        # a proxy object and JsonResponse() barfs on it, so we remove it
        for check in jason.get('data'):
            check.pop('DT_RowData', None)
        return JsonResponse(jason, safe=False)


@portal_auth_required(
    'BusinessOfficeFinance',
    'BusinessOfficeFinance', reverse_lazy('access_denied')
)
def cheque_list(request):
    return render(request, 'list.html', {
            'status': request.POST.get('status'),
            'codes': [
                settings.IMPORT_STATUS,
                settings.AUTO_REC,
                settings.REQUI_RICH,
                settings.SUSPICIOUS,
                settings.REQUI_VICH
            ]
        }
    )
