"""membresias_codigosur URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include, re_path
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from django.views.static import serve
from ajax_select import urls as ajax_select_urls

from async_notifications.markitup.views import preview_newsletter
from membership_manager.admin_memberships import MembInvoices, OrganizationInvoices, generate_invoice, build_pdf_invoice_view
from membership_manager.urls import urlpatterns as url_manager
from membership_telbot_manager.views import UpdateBot
from django.conf import settings
from djgentelella.urls import urlpatterns as djgentelellaurls
from matricula.urls import urlpatterns as enrollurls

urlpatterns = djgentelellaurls + [
    path('', RedirectView.as_view(url="/home/")),
    path('accounts/', include('allauth.urls')),
    path('async_notifications/', include('async_notifications.urls')),
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    path('telbot/', csrf_exempt(UpdateBot.as_view())),
    path('payments/membership/', MembInvoices.as_view()),
    path('payments/organization/', OrganizationInvoices.as_view()),
    path('invoice/generate/<int:pk>/', generate_invoice, name="generate_invoice"),
    path('invoice/build/<int:pk>/', build_pdf_invoice_view, name="build_pdf_invoice"),
    re_path(r'^ajax_select/', include(ajax_select_urls)),
    re_path(r'^media/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT,}
            ),
    re_path(r'^markitup/preview/$', login_required(preview_newsletter), name="markitup_preview"),
    url(r'^froala_editor/', include('froala_editor.urls')),
    ] + url_manager + enrollurls
