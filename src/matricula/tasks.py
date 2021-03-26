from django.utils import timezone
from django.conf import settings

from upo.celery import app

from matricula.contrib.bills.models import Bill
from matricula.models import Enroll

from async_notifications.utils import send_email_from_template


@app.task
def remove_invoices():
    """
    Create a invoice, at 60 days left - renewal expiration.
    """
    now=timezone.localdate(timezone.now())
    bills = Bill.objects.filter(is_paid=False, created_at__gt=now-timezone.timedelta(minutes=20))
    for bill in bills:
        send_email_from_template(
            'email_enroll_removed', bill.enrollment.student.user.email,
            {
                "group": bill.enrollment.group,
                'domain': settings.MY_PAYPAL_HOST,
            },
            enqueued=False, user=None)
    Enroll.objects.filter(bill__in=bills).delete()
    bills.delete()
