# encoding: utf-8
'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import url, include
from matricula.views.Auth import *
from matricula.views.Courses import *
from .admin import admin_site
from matricula.views.Pages import PageDetail
from matricula.views.Enrollments import *

urlpatterns = [
    url('^create_user$', create_user, name="create_user"),
    url('^confirm_email$', confirm_email, name="confirm_email"),
    url('^authenticate$', authenticate, name="authenticate"),
    url('^logout$', logout, name="logout"),
    url('^recover_password$', recover_password, name="recover_password"),
    url('^mail_recover_pass$', mail_recover_pass, name='mail_recover_pass'),
    url('^user/profile/(?P<pk>[0-9]+)/$', StudentEdit.as_view(), name='myprofile'),
    url('^courses$', list_courses, name='courses'),
    url('^course/(?P<pk>\d+)$', view_course, name='course'),


    url('^enrollme/(?P<pk>\d+)$', enrollme, name="enrollme"),
    url('^enrollment$', list_enroll, name="enrollment"),
    url('^finish_enroll/(?P<pk>\d+)$', finish_enroll, name="finish_enroll"),


    url(r'^admin/', include(admin_site.urls)),
    url(r'^pages/(?P<pk>\d+)$', PageDetail.as_view(), name="academica_pages"),
               ]