'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import patterns, url, include
from . import signals

urlpatterns = patterns('matricula.views',
                       url('^create_user$', 'create_user', name="create_user"),
                       url('^confirm_email$', 'confirm_email', name="confirm_email"),
                       url('^authenticate$', 'authenticate', name="authenticate"),
                       url('^logout$', 'logout', name="logout"),
                       url('^courses$', 'courses', name="courses"),
                       url('^course/(?P<pk>\d+)$', 'course', name="course"),
                       )

urlpatterns += patterns('matricula.enroll',
                        url('^enrollme/(?P<pk>\d+)$', 'enrollme', name="enrollme"),
                        url('^enrollment$', 'list_enroll', name="enrollment"),
                        url('^finish_enroll/(?P<pk>\d+)$', 'finish_enroll', name="finish_enroll"),
                        )

urlpatterns += patterns('matricula.bill_views',
                        url('^bills/$', 'get_my_bills', name="bills"),
                        )

urlpatterns += patterns('',
                        url(r'^something/paypal/', include('paypal.standard.ipn.urls')),
                        )