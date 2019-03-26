from django.contrib import admin
from django.conf.urls import  url
from django.views.generic import TemplateView

#django discovery
admin.autodiscover()
from djczech.reconciliation import views

urlpatterns = [
    url(
        r'^data/success/$',
        TemplateView.as_view(
            template_name='reconciliation/success.html'
        ),
        name='cheque_data_success'
    ),
    url(
        r'^data/$',
        views.cheque_data, name='cheque_data'
    ),
    url(
        r'^matching/$',
        views.cheque_matching, name='cheque_matching'
    ),
    url(
        r'^matching/ajax/$',
        views.cheque_matching_ajax, name='cheque_matching_ajax'
    ),
]
