from dateutil.relativedelta import relativedelta
from django.utils import timezone

from membership_manager.invoice_utils import create_invoice
from membership_manager.models import MembershipRenew


def create_renew(instance):
    now = timezone.now()
    renew = MembershipRenew.objects.create(membership=instance, creation_date=now,
                                   start_date=now,
                                   encobro=True,
                                   end_date=now + relativedelta(
                                       months=+instance.renewal_period.months)
                                   )
    create_invoice(renew)
    return renew