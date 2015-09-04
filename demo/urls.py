from django.conf.urls import patterns, url, include
from demo.views import render_temp, feature

urlpatterns = patterns('',
                       url('(?P<slug>features)/$', feature, name="feature"),
                       url('(?P<slug>[-\w]+)/$', render_temp, name="demo"),
                       )
