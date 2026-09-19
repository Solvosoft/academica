"""Pago de facturas con tarjeta mediante el servicio webcheckout."""
import hmac
import json
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..card_payments import apply_order_status, refresh_card_payment
from ..models import Bill, CardPayment
from ..webcheckout import WebCheckoutError, charge_amount, create_order

logger = logging.getLogger(__name__)

# El servicio expira las órdenes sin pagar a los 10 minutos.
REUSE_ORDER_MINUTES = 10


def _student_bill(request, pk):
    student = getattr(request.user, 'student', None)
    if student is None:
        raise Http404()
    return get_object_or_404(Bill, pk=pk, student=student)


@login_required
@require_POST
def pay_with_card(request, pk):
    if not settings.CARD_PAYMENTS_ENABLED:
        raise Http404()
    bill = _student_bill(request, pk)
    if bill.is_paid or bill.amount <= 0 or bill.enrollment is None:
        messages.info(request, "Esta factura no tiene pagos pendientes.")
        return redirect('bills')

    in_progress = bill.card_payments.exclude(status__in=CardPayment.TERMINAL_STATUSES).filter(
        created_at__gte=timezone.now() - timedelta(minutes=REUSE_ORDER_MINUTES)).first()
    if in_progress:
        return redirect(in_progress.checkout_url)

    try:
        order = create_order(bill)
    except WebCheckoutError:
        messages.error(request, "No fue posible iniciar el pago con tarjeta, por favor intente de nuevo "
                                "en unos minutos o utilice otro método de pago.")
        return redirect('bills')

    amount, currency = charge_amount(bill)
    card_payment = CardPayment.objects.create(
        bill=bill, order_id=order['id'], checkout_url=order['checkout_url'],
        amount=amount, currency=currency)
    # El estado que devuelve el servicio pasa por la misma lógica que el webhook.
    apply_order_status(card_payment, order)
    return redirect(order['checkout_url'])


@login_required
def card_payment_return(request, pk):
    """El estudiante vuelve del checkout: se consulta el estado real en el servicio."""
    bill = _student_bill(request, pk)
    card_payment = bill.card_payments.first()
    if card_payment is None:
        return redirect('bills')
    try:
        card_payment = refresh_card_payment(card_payment)
    except WebCheckoutError:
        pass

    if card_payment.status == CardPayment.Status.COMPLETED:
        messages.success(request, "Su pago con tarjeta fue aprobado, gracias. "
                                  "Le enviamos la confirmación por correo.")
    elif card_payment.is_terminal:
        messages.error(request, "El pago con tarjeta no se completó (%s). Puede intentarlo de nuevo."
                       % card_payment.get_status_display())
    else:
        messages.info(request, "Su pago con tarjeta está en proceso; le avisaremos por correo "
                               "cuando sea confirmado.")
    return redirect('bills')


def _valid_token(request):
    expected = settings.WEBCHECKOUT_NOTIFICATION_TOKEN
    if not expected:
        return True
    auth = request.headers.get('Authorization', '')
    prefix = 'Token '
    return auth.startswith(prefix) and hmac.compare_digest(auth[len(prefix):], expected)


@csrf_exempt
@require_POST
def card_payment_webhook(request):
    """
    Notificación del servicio en cada cambio de estado de una orden.

    No se confía en el estado que trae el cuerpo: se encola una consulta a la
    API del servicio, que es la que decide si la factura queda pagada.
    """
    if not _valid_token(request):
        return JsonResponse({'status': 'unauthorized'}, status=401)
    try:
        payload = json.loads(request.body or b'{}')
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")
    order_id = payload.get('order_id') if isinstance(payload, dict) else None
    if not order_id:
        return HttpResponseBadRequest("Missing order_id")
    try:
        card_payment = CardPayment.objects.get(order_id=order_id)
    except (CardPayment.DoesNotExist, ValidationError):
        return JsonResponse({'status': 'not found'}, status=404)

    from matricula.tasks import refresh_card_payment_task
    transaction.on_commit(lambda: refresh_card_payment_task.delay(card_payment.pk))
    return JsonResponse({'status': 'ok'})
