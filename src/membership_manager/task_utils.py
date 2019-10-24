from decimal import Decimal

from async_notifications.utils import send_email_from_template
from django.utils import timezone

from membership_manager.admin_memberships import filter_memb_queryset


from membership_manager.admin_pdf import invoice_expiration_filter_queryset, renewal_expiration_filter_manager
from membership_manager.models import Membership, Invoice, MembershipRenew

def notify_invoice_expiration(now):
    """
    Gets the membership invoices and notify if there is any in the expiration range.
    """
    qset = Invoice.objects.all()
    notify_qset = invoice_expiration_filter_queryset(qset)  # Specific remaining days

    for invoice in notify_qset:
        if invoice.membership.contact:
            email = invoice.membership.contact.email
        else:
            email = invoice.membership.organization.contact.email
        send_email_from_template('notification_mail', [email],
                                 context={
                                     'membership': invoice.membership
                                 },
                                 enqueued=True,
                                 user=None,
                                 upfile=None)