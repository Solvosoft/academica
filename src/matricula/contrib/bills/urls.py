'''
Created on 7/4/2015

@author: luisza
'''

from django.urls import include, path, re_path

from matricula.contrib.bills.views.Bills import get_my_bills, pay_using_sinpemovil, pay_using_banktransfer
from .views.admin_views import BillList, create_bill, edit_bill, BillDelete

urlpatterns = [
    re_path(r'^bills/$', get_my_bills, name="bills"),
    re_path(r'^bills/paybills/paypal/', include('paypal.standard.ipn.urls')),
    path('bills/paybills/sinpemovil/', pay_using_sinpemovil, name="pay_using_sinpemovil"),
    path('bills/paybills/banktransfer/', pay_using_banktransfer, name="pay_using_banktransfer"),
    re_path(r'^bills/list$', BillList.as_view(), name="listbills"),
    re_path(r'^bills/create_bill$', create_bill, name="create_bill"),
    path('bills/delete_bill/<int:pk>/', BillDelete.as_view() , name="delete_bill"),
    path('bills/edit_bill/<int:pk>/', edit_bill, name="edit_bill"),
]
