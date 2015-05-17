'''
Created on 7/5/2015

@author: luisza
'''


from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
from django.shortcuts import render
from matricula.models import Bill
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def get_my_bills(request):
    all_bills = Bill.objects.filter(student=request.user).order_by('paid_date')
    paid = all_bills.filter(is_paid=True)
    not_paid = all_bills.filter(is_paid=False)

    not_paid_forms = []
    for bill in not_paid:
        not_paid_forms.append(
            {'obj': bill,
             'form': PayPalPaymentsForm(initial={
                    "business": settings.PAYPAL_RECEIVER_EMAIL,
                    "amount": str(bill.amount),
                    "item_name": bill.short_description,
                    "invoice": str(bill.pk),
                    "notify_url": settings.MY_PAYPAL_HOST + reverse('paypal-ipn'),
                    "return_url": settings.MY_PAYPAL_HOST + reverse('bills'),
                    "cancel_return": settings.MY_PAYPAL_HOST + reverse('bills'),
                    })
             }
        )

    return render(request, 'bills.html', {'paid': paid,
                                   'not_paid': not_paid_forms})
    
