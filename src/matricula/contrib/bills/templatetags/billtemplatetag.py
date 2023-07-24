from django import template

from matricula.contrib.bills.forms import SinpeMovilBillForm, BankBillForm
from matricula.contrib.bills.models import SinpeMovilBill, BankBill

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