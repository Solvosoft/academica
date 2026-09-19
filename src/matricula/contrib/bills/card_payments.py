"""Aplicación del estado de los pagos con tarjeta a las facturas."""
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.html import mark_safe

from djgentelella.async_notification.sending import send_email_from_template

from .models import Bill, CardPayment
from .webcheckout import get_order

logger = logging.getLogger(__name__)


def mark_bill_paid(bill, transaction_id):
    """Marca la factura como pagada y avisa al estudiante (una sola vez)."""
    bill.is_paid = True
    bill.paid_date = timezone.now()
    bill.transaction_id = transaction_id
    bill.save(update_fields=['is_paid', 'paid_date', 'transaction_id'])
    transaction.on_commit(lambda: send_email_from_template(
        'email_invoice_academy', bill.student.user.email, {
            'bill': bill,
            'domain': settings.SITE_BASE_URL,
            'bill_description_safe': mark_safe(bill.description),
            'student': bill.student,
        },
        enqueued=False,
        user=None))


def apply_order_status(card_payment, data):
    """
    Actualiza el pago con los datos de la orden devueltos por el servicio.

    Es idempotente: un pago en estado terminal no cambia más, y la factura solo
    se marca pagada una vez.
    """
    with transaction.atomic():
        card_payment = CardPayment.objects.select_for_update().get(pk=card_payment.pk)
        if card_payment.is_terminal:
            return card_payment
        status = data.get('status', card_payment.status)
        if status not in CardPayment.Status.values:
            logger.warning("Estado desconocido %s para la orden %s", status, card_payment.order_id)
            return card_payment
        card_payment.status = status
        card_payment.status_reason = data.get('status_reason') or ''
        card_payment.authorization_code = data.get('authorization_code') or ''
        card_payment.save(update_fields=['status', 'status_reason', 'authorization_code', 'updated_at'])

        if status == CardPayment.Status.COMPLETED:
            bill = Bill.objects.select_for_update().get(pk=card_payment.bill_id)
            if not bill.is_paid:
                mark_bill_paid(bill, "Tarjeta %s %s" % (
                    card_payment.order_id, card_payment.authorization_code))
    return card_payment


def refresh_card_payment(card_payment):
    """Consulta el estado de la orden en el servicio y lo aplica."""
    return apply_order_status(card_payment, get_order(card_payment.order_id))
