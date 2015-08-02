'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import patterns, url, include
from . import signals
from .views.stripe import stripe_charge

urlpatterns = patterns('matricula.contrib.bills.views.Bills',
                        url('^bills/$', 'get_my_bills', name="bills"),
                        )

urlpatterns += patterns('',
                        url(r'^paybills/paypal/', include('paypal.standard.ipn.urls')),
                        url(r'^charge/(?P<pk>\d+)$', stripe_charge, name="stripe_charge"),
                        )
