from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView


urlpatterns = [
    # Examples:
    # url(r'^$', 'academica.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url('^$', RedirectView.as_view(url='/matricula/courses', permanent=False), name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^matricula/', include('matricula.urls')),
    url(r'^matricula_bills/', include('matricula.contrib.bills.urls')),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url('^accounts/profile/?$', 'matricula.views.Auth.get_profile'),
]
