# encoding: utf-8
'''
Created on 17/5/2015

@author: luisza
'''

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from paypal.standard.forms import PayPalPaymentsForm

from matricula.contrib.bills.forms import SinpeMovilBillForm, BankBillForm
from matricula.contrib.bills.models import Bill


def get_amount(bill):
    """Monto de la factura en dólares (PayPal cobra en USD)."""
    return bill.amount / bill.currency.rates


@csrf_exempt
@login_required
def get_my_bills(request):
    if hasattr(request.user, 'student'):
        all_bills = Bill.objects.filter(
            student=request.user.student).order_by('paid_date')
        paid = all_bills.filter(is_paid=True)
        not_paid = all_bills.filter(is_paid=False, enrollment__paid_excluded=False)

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

@login_required
def pay_using_sinpemovil(request):
    form = SinpeMovilBillForm(request.POST)
    if form.is_valid():
        form.save()
        send_mail("New SinpeMovil payment for a course %s"%(form.cleaned_data['bill'].student),
            "Please check %s to see details for course %s"%(request.get_host(), form.cleaned_data['group_name']),
            None,
            settings.PAYMENT_NOTIFICATION_MAIL

        )
        messages.success(request, "Recibimos su reporte de pago; lo verificaremos pronto.")
    else:
        messages.error(request, "Hubo un error procesando su solicitud, por favor vuelva a intentarlo")
    return redirect(reverse('bills'))

@login_required
def pay_using_banktransfer(request):
    form = BankBillForm(request.POST, files=request.FILES)
    if form.is_valid():
        form.save()
        send_mail("New Bank payment from %s"%(form.cleaned_data['bill'].student),
            "Please check %s to see details for course %s"%(request.get_host(), form.cleaned_data['group_name']),
            None,
            settings.PAYMENT_NOTIFICATION_MAIL
        )
        messages.success(request, "Recibimos su reporte de pago; lo verificaremos pronto.")
    else:
        messages.error(request,
                       "Hubo un error procesando su solicitud, por favor vuelva a intentarlo, recuerde adjuntar el comprobante %s"%(
                           form.errors
                       ))
    return redirect(reverse('bills'))

