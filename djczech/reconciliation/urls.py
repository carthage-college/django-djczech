from django.contrib import admin
from django.conf.urls import patterns, url
from django.views.generic import TemplateView

#django discovery
admin.autodiscover()

urlpatterns = patterns('djczech.reconciliation.views',
    url(
        r'^check/(?P<cid>\d+)/$',
        'check_detail', name="check_detail"
    ),
    url(
        r'^check/search/$',
        'check_search', name="check_search"
    ),
    url(
        r'^check/success/$',
        TemplateView.as_view(
            template_name='reconciliation/success.html'
        ),
        name='check_success'
    ),
)
