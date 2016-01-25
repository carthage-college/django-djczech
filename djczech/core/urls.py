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
        r'^accounts/login/$',auth_views.login,
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
    # admin
    url(
        r'^admin/', include(admin.site.urls)
    ),
    # cheque requi
    url(
        r'^reconciliation/', include("djczech.reconciliation.urls")
    )
)

urlpatterns += patterns('djczech.core.views',
    # detailed view
    url(
        r'^detail/(?P<sid>\d+)/$',
        'cheque_detail', name="cheque_detail"
    ),
    # dynamically load data
    url(
        r'^ajax/$',
        'cheque_ajax', name="cheque_ajax"
    ),
    # list cheques
    url(
        r'^list/$',
        'cheque_list', name="cheque_list"
    ),
    # direct to template
    url(
        r'^denied/$',
        TemplateView.as_view(
            template_name="denied.html"
        ), name="access_denied"
    ),
    # redirect
    url(
        r'^$', RedirectView.as_view(url="/djczech/reconciliation/data/")
    )
)
