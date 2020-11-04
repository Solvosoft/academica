'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import url, include
from matricula.contrib.bills.views.Bills import get_my_bills
from django.urls import path
from matricula.views.admin_views import GroupList, create_group, GroupDelete, edit_group
from .views.admin_views import ColonExchangeList, create_colonexchange, ColonExchangeDelete,\
    edit_colonexchange, BillList, create_bill, edit_bill, BillDelete


urlpatterns = [
    url('^bills/$', get_my_bills, name="bills"),
    url(r'^paybills/paypal/', include('paypal.standard.ipn.urls')),
    url('list', BillList.as_view(), name="listbills"),
    url('create_bill', create_bill, name="create_bill"),
    path('delete_bill/<int:pk>/', BillDelete.as_view() , name="delete_bill"),
    path('edit_bill/<int:pk>/', edit_bill, name="edit_bill"),
    url('colonexchanges', ColonExchangeList.as_view(), name="colonexchange"),
    url('create_colonexchange', create_colonexchange, name="create_colonexchange"),
    path('delete_colonexchange/<int:pk>/', ColonExchangeDelete.as_view() , name="delete_colonexchange"),
    path('edit_colonexchange/<int:pk>/', edit_colonexchange, name="edit_colonexchange"),
]
