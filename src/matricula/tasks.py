from datetime import  timedelta

from django.utils import timezone as datetime
from django.conf import settings
from django.core.management import call_command

from djgentelella.async_notification.sending import send_email_from_template

from matricula.certificate_utils import build_pdf_certificate
from academica.celery import app
from matricula.contrib.bills.card_payments import refresh_card_payment
from matricula.contrib.bills.models import Bill, CardPayment
from matricula.contrib.bills.webcheckout import WebCheckoutError
from matricula.models import Enroll


@app.task
def process_async_notifications():
    """Envía los correos encolados (``enqueued=True``) de djgentelella."""
    call_command('process_notifications')


@app.task(bind=True, max_retries=3, default_retry_delay=60)
def refresh_card_payment_task(self, card_payment_pk):
    """Consulta en el servicio de pagos el estado de una orden con tarjeta."""
    card_payment = CardPayment.objects.filter(pk=card_payment_pk).first()
    if card_payment is None or card_payment.is_terminal:
        return
    try:
        refresh_card_payment(card_payment)
    except WebCheckoutError as exc:
        raise self.retry(exc=exc)


@app.task
def poll_card_payments():
    """Respaldo del webhook: revisa las órdenes con tarjeta que siguen abiertas."""
    now = datetime.now()
    pending = CardPayment.objects.exclude(status__in=CardPayment.TERMINAL_STATUSES).filter(
        created_at__lte=now - timedelta(minutes=2), created_at__gte=now - timedelta(days=1))
    for card_payment in pending:
        try:
            refresh_card_payment(card_payment)
        except WebCheckoutError:
            pass


@app.task
def remove_invoices():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    now=datetime.now()
    bills = Bill.objects.filter(
        is_paid=False, enrollment__paid_excluded=False,
        created_at__lte=now-timedelta(hours=settings.HOURS_TO_PAY)).exclude(
        # no se borra una matrícula con un pago con tarjeta en curso o aprobado
        card_payments__status__in=[CardPayment.Status.IN_PROCESS, CardPayment.Status.COMPLETED])
    for bill in bills:
        send_email_from_template(
            'email_enroll_removed', bill.enrollment.student.user.email,
            {
                "group": bill.enrollment.group,
                'domain': settings.MY_PAYPAL_HOST,
                'hours_to_pay': settings.HOURS_TO_PAY,
            },
            enqueued=False, user=None)
    Enroll.objects.filter(bill__in=bills).delete()
    bills.delete()


@app.task
def task_generate_group_certificate(group):
    for enroll in Enroll.objects.filter(group__pk=group, course_status="approved", enroll_finished=True):
        try:
            build_pdf_certificate(enroll)
        except Exception as e:
            print("Error generando certificado: ",enroll.pk, e)
            pass