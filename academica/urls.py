from django.conf.urls import include, url
from django.contrib import admin
from matricula.views import index
from matricula.views.Auth import *

urlpatterns = [
    # Examples:
    # url(r'^$', 'academica.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url('^$', index, name='index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^matricula/', include('matricula.urls')),
    url(r'^matricula_bills/', include('matricula.contrib.bills.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url('^accounts/profile/?$', get_profile),
]
