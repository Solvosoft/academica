from datetime import timedelta

from async_notifications.utils import send_email_from_template

from membership_manager.admin_pdf import invoice_expiration_filter_queryset
from membership_manager.models import Invoice, MembershipRenew
from membership_manager.render_pdf import generate_invoice


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


def invoice_creation(now):
    renews = MembershipRenew.objects.filter(end_date__lte=now + timedelta(days=60),
                                            active=True,
                                            graceperiod=False,
                                            membership__state="active",
                                            inv_m_renews=None
                                            )
    for renew in renews:
        invoice = Invoice.objects.create(creation_date=now,
                                         expiration_date=renew.end_date,
                                         payment_date=renew.end_date,
                                         membership=renew.membership,
                                         renewal_period=renew,
                                         description=f'{renew.membership.name} expira al {renew.end_date}. Debe ser pagada.',
                                         amount=renew.membership.annual_cost,
                                         currency=renew.membership.currency,
                                         status='pending')
        generate_invoice(invoice.membership, invoice, email_template="notification_mail", enqueued=True)


def renew_graceperiod(now):
    renews = MembershipRenew.objects.filter(end_date=now,
                                            active=True,
                                            graceperiod=False,
                                            membership__state="active"
                                            )

    for renew in renews:
        membership = renew.membership
        MembershipRenew.objects.create(
            creation_date=now,
            membership=renew.membership,
            start_date=now,
            end_date=now + timedelta(days=60),
            graceperiod=True,
            active=True
        )
        membership.state = "graceperiod"
        membership.save()


def membership_deactivating(now):
    renews = MembershipRenew.objects.filter(end_date=now,
                                            active=True,
                                            graceperiod=True,
                                            membership__state="graceperiod"
                                            )
    for renew in renews:
        membership = renew.membership
        if membership.contact:
            email = membership.contact.email
        else:
            email = membership.organization.contact.email
        send_email_from_template('expiration_mail', [email],
                                 context={
                                     'membership': membership
                                 },
                                 enqueued=True,
                                 user=None,
                                 upfile=None)

        membership.state = "inactive"
        membership.save()
        MembershipRenew.objects.filter(membership=membership).update(state="inactive")
