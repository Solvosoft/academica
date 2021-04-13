from datetime import  timedelta

from django.utils import timezone as datetime
from django.conf import settings

from async_notifications.utils import send_email_from_template

from upo.celery import app
from matricula.contrib.bills.models import Bill
from matricula.models import Enroll


@app.task
def remove_invoices():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    now=datetime.now()
    bills = Bill.objects.filter(
        is_paid=False, enrollment__paid_excluded=False,
        created_at__lte=now-timedelta(hours=settings.HOURS_TO_PAY))
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
