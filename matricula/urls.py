'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import patterns, url, include
from django.contrib.auth import views as auth_views

urlpatterns = patterns('matricula.views.Auth',
                       url('^create_user$', 'create_user', name="create_user"),
                       url('^confirm_email$', 'confirm_email', name="confirm_email"),
                       url('^authenticate$', 'authenticate', name="authenticate"),
                       url('^logout$', 'logout', name="logout"),
                       )

urlpatterns += patterns('matricula.views.Courses',
                       url('^courses$', 'list_courses', name="courses"),
                       url('^course/(?P<pk>\d+)$', 'view_course', name="course"),
                       )

urlpatterns += patterns('matricula.views.Enrollments',
                        url('^enrollme/(?P<pk>\d+)$', 'enrollme', name="enrollme"),
                        url('^enrollment$', 'list_enroll', name="enrollment"),
                        url('^finish_enroll/(?P<pk>\d+)$', 'finish_enroll', name="finish_enroll"),
                        )

urlpatterns += patterns('',
                        url(r'^accounts/login/$', auth_views.login, name="login"),
                        )
