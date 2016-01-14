from django.contrib import admin
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

#django discovery
admin.autodiscover()

urlpatterns = patterns('djczech.reconciliation.views',
    url(
        r'^cheque/(?P<cid>\d+)/detail/$',
        'cheque_detail', name="cheque_detail"
    ),
    url(
        r'^cheque/ajax/$',
        'cheque_ajax', name="cheque_ajax"
    ),
    url(
        r'^cheque/data/$',
        'cheque_data', name="cheque_data"
    ),
    url(
        r'^cheque/list/$',
        'cheque_list', name="cheque_list"
    ),
    url(
        r'^cheque/search/$',
        'cheque_detail', name="cheque_search"
    ),
    url(
        r'^cheque/success/$',
        TemplateView.as_view(
            template_name='reconciliation/cheque/success.html'
        ),
        name='cheque_data_success'
    ),
    url(
        r'^cheque/matching/$',
        TemplateView.as_view(
            template_name='reconciliation/cheque/matching.html'
        ),
        name='cheque_matching'
    ),
)
