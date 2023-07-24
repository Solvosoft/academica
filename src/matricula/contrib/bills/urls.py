'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import url, include
from django.urls import path

from matricula.contrib.bills.views.Bills import get_my_bills, pay_using_sinpemovil, pay_using_banktransfer
from .views.admin_views import ColonExchangeList, create_colonexchange, ColonExchangeDelete, \
    edit_colonexchange, BillList, create_bill, edit_bill, BillDelete

urlpatterns = [
    url('bills/$', get_my_bills, name="bills"),
    url(r'^bills/paybills/paypal/', include('paypal.standard.ipn.urls')),
    path('bills/paybills/sinpemovil/', pay_using_sinpemovil, name="pay_using_sinpemovil"),
    path('bills/paybills/banktransfer/', pay_using_banktransfer, name="pay_using_banktransfer"),
    url('bills/list', BillList.as_view(), name="listbills"),
    url('bills/create_bill', create_bill, name="create_bill"),
    path('bills/delete_bill/<int:pk>/', BillDelete.as_view() , name="delete_bill"),
    path('bills/edit_bill/<int:pk>/', edit_bill, name="edit_bill"),
    url('bills/colonexchanges', ColonExchangeList.as_view(), name="colonexchange"),
    url('bills/create_colonexchange', create_colonexchange, name="create_colonexchange"),
    path('bills/delete_colonexchange/<int:pk>/', ColonExchangeDelete.as_view() , name="delete_colonexchange"),
    path('bills/edit_colonexchange/<int:pk>/', edit_colonexchange, name="edit_colonexchange"),
]
