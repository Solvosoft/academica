"""
Reglas de los cupones de descuento.

Un estudiante puede tener en un grupo, como máximo, un 100 % de descuento: un
cupón del 100 % o dos del 50 %. Los cupones se aplican a la factura del grupo
(si ya existe) o cuando se crea (señal ``create_bill``). Una factura cuyo total
queda en 0 se marca como pagada.
"""
import random
import string
from decimal import Decimal

from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import smart_str

from matricula.models import Coupon

MAX_PERCENTAGE = 100


COUPON_TRANSACTION = 'Cupón'


def coupons_total(student, group, exclude=None):
    coupons = Coupon.objects.filter(student=student, group=group)
    if exclude is not None:
        coupons = coupons.exclude(pk=exclude.pk)
    return coupons.aggregate(total=Sum('discount_percentage'))['total'] or 0


def can_add(student, group, percentage, exclude=None):
    return coupons_total(student, group, exclude) + int(percentage) <= MAX_PERCENTAGE


def paid_with_money(bill):
    """La factura se pagó con dinero (no solo con cupones): sus cupones ya no se tocan."""
    return bill is not None and bill.is_paid and bill.transaction_id != COUPON_TRANSACTION


def make_code(student, group, percentage):
    """
    Código único con el formato histórico ``UP<año><XX>P[2]<porcentaje><YY>``:
    la ``P2`` (posición 9) marca el segundo cupón del 50 % del mismo grupo.
    """
    second = Coupon.objects.filter(student=student, group=group, discount_percentage=50).exists()
    year = timezone.now().year
    while True:
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        suffix = ''.join(random.choices(string.ascii_uppercase, k=2))
        code = "UP%d%sP%s%d%s" % (year, letters, '2' if second else '', int(percentage), suffix)
        if not Coupon.objects.filter(code=code).exists():
            return code


def create_coupon(student, group, percentage):
    """Crea el cupón (valida el máximo) y lo aplica a la factura si ya existe."""
    if not can_add(student, group, percentage):
        return None
    coupon = Coupon.objects.create(student=student, group=group, discount_percentage=int(percentage),
                                   code=make_code(student, group, percentage))
    bill = coupon_bill(student, group)
    if bill is not None:
        apply_coupons(bill)
        coupon.refresh_from_db()
    return coupon


def coupon_bill(student, group):
    from matricula.contrib.bills.models import Bill
    return Bill.objects.filter(student=student, enrollment__group=group, is_paid=False).first()


def apply_coupons(bill):
    """Recalcula el monto de la factura con todos los cupones del estudiante en el grupo."""
    group = bill.enrollment.group
    coupons = Coupon.objects.filter(student=bill.student, group=group)
    percentage = min(sum(c.discount_percentage or 0 for c in coupons), MAX_PERCENTAGE)
    cost = Decimal(group.cost)
    discount = (cost * Decimal(percentage) / Decimal(100)).quantize(Decimal('0.01'))
    total = cost - discount
    bill.amount = total
    bill.description = render_to_string('invoice_enroll.html', {
        'student': bill.student,
        'enroll': smart_str(group),
        'discount': discount,
        'total': total,
        'date': bill.enrollment.enroll_date.strftime("%Y-%m-%d %H:%M"),
        'group': group,
    })
    if total <= 0 and not bill.is_paid:
        # Beca completa: no hay nada que cobrar ni una matrícula que vencer.
        bill.is_paid = True
        bill.paid_date = timezone.now()
        bill.transaction_id = COUPON_TRANSACTION
    elif total > 0 and bill.is_paid and bill.transaction_id == COUPON_TRANSACTION:
        # Se quitó la beca completa: la factura vuelve a estar pendiente.
        bill.is_paid = False
        bill.transaction_id = None
    bill.save()
    coupons.update(bill=bill, is_used=True)
    return bill


def _bill_for(student, group):
    from matricula.contrib.bills.models import Bill
    return Bill.objects.filter(student=student, enrollment__group=group).order_by('-pk').first()


def update_coupon(coupon, student, group, percentage):
    """
    Cambia estudiante, grupo o porcentaje de un cupón y recalcula las facturas
    afectadas. Devuelve un mensaje de error o ``None`` si se guardó.
    """
    percentage = int(percentage)
    if paid_with_money(coupon.bill):
        return "El cupón ya se aplicó a una factura pagada; no se puede modificar."
    if not can_add(student, group, percentage, exclude=coupon):
        return "Error el usuarie %s ya tiene el 100%% de cupones en este curso" % student
    old_bill = coupon.bill or _bill_for(coupon.student, coupon.group)
    if (student, group, percentage) != (coupon.student, coupon.group, coupon.discount_percentage):
        coupon.student, coupon.group, coupon.discount_percentage = student, group, percentage
        coupon.code = make_code(student, group, percentage)
    coupon.bill, coupon.is_used = None, False
    coupon.save()
    new_bill = _bill_for(student, group)
    for bill in {b.pk: b for b in (old_bill, new_bill) if b is not None and not paid_with_money(b)}.values():
        apply_coupons(bill)
    return None


def delete_coupon(coupon):
    """Elimina el cupón y recalcula la factura a la que estaba aplicado."""
    if paid_with_money(coupon.bill):
        return "El cupón ya se aplicó a una factura pagada; no se puede eliminar."
    bill = coupon.bill or _bill_for(coupon.student, coupon.group)
    coupon.delete()
    if bill is not None and not paid_with_money(bill):
        apply_coupons(bill)
    return None
