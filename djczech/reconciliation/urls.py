from django.contrib import admin
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from djtools.decorators.auth import group_required, portal_auth_required

#django discovery
admin.autodiscover()

urlpatterns = patterns('djczech.reconciliation.views',
    url(
        r'^data/$',
        'cheque_data', name="cheque_data"
    ),
    url(
        r'^data/success/$',
        TemplateView.as_view(
            template_name='reconciliation/success.html'
        ),
        name='cheque_data_success'
    ),
    url(
        r'^matching/$',
        group_required(lambda u: 'BusinessOfficeFinance')(TemplateView.as_view(
            template_name='reconciliation/matching.html'
        )),
        name='cheque_matching'
    ),
)
