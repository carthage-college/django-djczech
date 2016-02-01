from django.contrib import admin
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from djtools.decorators.auth import group_required, portal_auth_required

#django discovery
admin.autodiscover()

urlpatterns = patterns('djczech.reconciliation.views',
    url(
        r'^data/success/$',
        TemplateView.as_view(
            template_name='reconciliation/success.html'
        ),
        name='cheque_data_success'
    ),
    url(
        r'^data/$',
        'cheque_data', name="cheque_data"
    ),
    url(
        r'^matching/$',
        'cheque_matching', name='cheque_matching'
    ),
    url(
        r'^matching/ajax/$',
        'cheque_matching_ajax', name='cheque_matching_ajax'
    ),
)
