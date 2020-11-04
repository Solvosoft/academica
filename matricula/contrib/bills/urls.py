'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import url, include
from matricula.contrib.bills.views.Bills import get_my_bills
from django.urls import path
from matricula.views.admin_views import GroupList, create_group, GroupDelete, edit_group


urlpatterns = [
    url('^bills/$', get_my_bills, name="bills"),
    url(r'^paybills/paypal/', include('paypal.standard.ipn.urls')),
    url('list', GroupList.as_view(), name="listbills"),
    url('create_bill', create_group, name="create_bill"),
    path('delete_bill/<int:pk>/', GroupDelete.as_view() , name="delete_bill"),
    path('edit_bill/<int:pk>/', edit_group, name="edit_bill"),
    url('colonexchanges', GroupList.as_view(), name="colonexchange"),
    url('create_colonexchange', create_group, name="create_colonexchange"),
    path('delete_colonexchange/<int:pk>/', GroupDelete.as_view() , name="delete_colonexchange"),
    path('edit_colonexchange/<int:pk>/', edit_group, name="edit_colonexchange"),
]
