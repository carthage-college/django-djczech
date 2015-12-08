from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView, TemplateView

from djauth.views import loggedout
from djtools.views.dashboard import responsive_switch

admin.autodiscover()

handler404 = 'djtools.views.errors.four_oh_four_error'
handler500 = 'djtools.views.errors.server_error'

urlpatterns = patterns('',
    # auth
    url(
        r'^accounts/login',auth_views.login,
        {'template_name': 'accounts/login.html'},
        name='auth_login'
    ),
    url(
        r'^accounts/logout/$',auth_views.logout,
        {'next_page': reverse_lazy("auth_loggedout")},
        name="auth_logout"
    ),
    url(
        r'^accounts/loggedout',loggedout,
        {'template_name': 'accounts/logged_out.html'},
        name="auth_loggedout"
    ),
    url(
        r'^accounts/$',
        RedirectView.as_view(url=reverse_lazy("auth_login"))
    ),
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
    # direct to template
    url(
        r'^denied/$',
        TemplateView.as_view(
            template_name="reconciliation/denied.html"
        ), name="access_denied"
    ),
    # ajax post method to save various types characteristics to db and session
    url(
        r'^set-val/$', 'djczech.core.views.set_val', name="set_val"
    ),
    # override mobile first responsive UI
    url(
        r'^responsive/(?P<action>[-\w]+)/',
        'responsive_switch', name="responsive_switch"
    ),
    # redirect
    url(
        r'^$', RedirectView.as_view(url="/djczech/reconciliation/")
    ),
)
