import datetime, calendar
from django.utils.timezone import now as timezonenow
from django.core.management import BaseCommand

from membership_manager import task_utils as utils


def get_day_month(now=None):
    if now is None:
        now = timezonenow()

    num_days = calendar.monthrange(now.year, now.month)[1]
    return [datetime.datetime(now.year, now.month, day) for day in range(1, num_days + 1)]


class Command(BaseCommand):
    help = "Genera las acciones"

    def handle(self, *args, **options):
        days = get_day_month()
        for now in days:
            print("notify_invoice_expiration")
            utils.notify_invoice_expiration(now)
            print("invoice_creation")
            utils.invoice_creation(now)
            print("renew_graceperiod")
            utils.renew_graceperiod(now)
            print("membership_deactivating")
            utils.membership_deactivating(now)