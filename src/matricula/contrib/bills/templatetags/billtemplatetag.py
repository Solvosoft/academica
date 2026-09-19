from django import template

from matricula.contrib.bills.forms import SinpeMovilBillForm, BankBillForm
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from matricula.contrib.bills.models import SinpeMovilBill, BankBill, CardPayment
from matricula.contrib.bills.webcheckout import charge_amount

register = template.Library()


@register.simple_tag
def sinpemovil_form(bill):
    bill = bill['obj']
    smb = SinpeMovilBill.objects.filter(bill=bill).first()
    student = bill.enrollment.student.user.get_full_name()
    group_name=str(bill.enrollment.group.course) +' -- '+str(bill.enrollment.group)
    if  smb:
        if smb.verified:
            return "Pago verificado correctamente"

        return "Pago pendiente de verificar, pronto será verificado por nuestro personal"

    form = SinpeMovilBillForm(initial={'bill': bill.pk, 'group_name': group_name, 'name': student})
    return form.as_horizontal

@register.simple_tag
def bank_form(bill):
    bill = bill['obj']
    student = bill.enrollment.student.user.get_full_name()
    group_name=str(bill.enrollment.group.course) +' -- '+str(bill.enrollment.group)
    smb = BankBill.objects.filter(bill=bill.pk).first()
    if smb:
        if smb.verified:
            return "Pago verificado correctamente"

        return "Pago pendiente de verificar, pronto será verificado por nuestro personal"

    form = BankBillForm(initial={'bill': bill, 'group_name': group_name, 'name': student})
    return form.as_horizontal

@register.simple_tag
def have_payment_verification(bill):
    smb = SinpeMovilBill.objects.filter(bill=bill.pk).first()
    if smb:
        return smb
    bb = BankBill.objects.filter(bill=bill.pk).first()
    if bb:
        return bb
    return False

@register.simple_tag
def card_payment(bill):
    """Datos para pagar la factura con tarjeta, o None si el método no está activo."""
    bill = bill['obj']
    if not settings.CARD_PAYMENTS_ENABLED or bill.amount <= 0:
        return None
    amount, currency = charge_amount(bill)
    in_progress = bill.card_payments.exclude(status__in=CardPayment.TERMINAL_STATUSES).filter(
        created_at__gte=timezone.now() - timedelta(minutes=10)).first()
    return {'amount': amount, 'currency': currency, 'in_progress': in_progress,
            'last': bill.card_payments.first()}
