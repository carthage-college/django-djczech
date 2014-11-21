from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView, TemplateView

from django.contrib import admin

admin.autodiscover()

handler404 = 'djtools.views.errors.four_oh_four_error'
handler500 = 'djtools.views.errors.server_error'

urlpatterns = patterns('',
    url(
        r'^admin/', include(admin.site.urls)
    ),
    # my app
    url(
        r'^reconciliation/', include("djczech.reconciliation.urls")
    ),
    # direct to template
    url(
        r'^success/$',
        TemplateView.as_view(
            template_name="reconciliation/success.html"
        )
    ),
    # redirect
    url(
        r'^$', RedirectView.as_view(url="/djczech/reconciliation/")
    ),
)
