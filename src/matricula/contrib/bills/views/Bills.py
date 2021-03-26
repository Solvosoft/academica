# encoding: utf-8
'''
Created on 17/5/2015

@author: luisza
'''

from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.shortcuts import render
from matricula.contrib.bills.models import Bill
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from membership_core.models import SystemCurrency


def get_amount(bill):
    currency = SystemCurrency.objects.get(currency=bill.currency)
    return bill.amount / currency.rates


@csrf_exempt
@login_required
def get_my_bills(request):
    if hasattr(request.user, 'student'):
        all_bills = Bill.objects.filter(
            student=request.user.student).order_by('paid_date')
        paid = all_bills.filter(is_paid=True)
        not_paid = all_bills.filter(is_paid=False)

        not_paid_forms = []
        for bill in not_paid:
            amount = get_amount(bill)
            not_paid_forms.append(
                {
                    'obj': bill,
                    'form': PayPalPaymentsForm(initial={
                        "business": settings.PAYPAL_RECEIVER_EMAIL,
                        "amount": "%.2f" % (amount),
                        "currency_code": 'USD',
                        "item_name": str(bill.enrollment.group.pk),
                        "invoice": str(bill.pk),
                        "item_number": str(bill.enrollment.student.pk),
                        "notify_url":
                            settings.MY_PAYPAL_HOST + reverse('paypal-ipn'),
                        "return_url": settings.MY_PAYPAL_HOST + reverse('bills'),
                        "cancel_return":
                            settings.MY_PAYPAL_HOST + reverse('bills'),
                    })
                }
            )

        return render(
            request, 'bills.html', {'paid': paid, 'not_paid': not_paid_forms})
    paid = Bill.objects.none()
    not_paid_forms = []
    return render(
            request, 'bills.html', {'paid': paid, 'not_paid': not_paid_forms})    
