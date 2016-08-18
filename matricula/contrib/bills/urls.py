'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import url, include
from matricula.contrib.bills.views.Bills import *

urlpatterns = [ url('^bills/$', get_my_bills, name="bills"),


     url(r'^paybills/paypal/', include('paypal.standard.ipn.urls')),
                        ]
