from datetime import timedelta

from django.utils import timezone
from django.utils.timezone import now

from membership_manager.models import Invoice
from membership_manager.render_pdf import build_pdf_invoice, generate_invoice
from membership_manager.utils import stringcode_generator, membership_payment_manager


def create_invoice(renew, startdate=None):

    startdate = startdate if startdate is not None else now()
    expiration = startdate + timedelta(days=60)
    invoice = Invoice.objects.create(creation_date=now(),
                                     expiration_date=expiration,
                                     membership=renew.membership,
                                     renewal_period=renew,
                                     description=f'{renew.membership.name} expira al {renew.end_date}. Debe ser pagada.',
                                     amount=renew.membership.annual_cost,
                                     currency=renew.membership.currency,
                                     status='pending')
    string_code = stringcode_generator()
    invoice.code = f'%s-%s' % (string_code, str(invoice.pk).rjust(6, "0"))
    build_pdf_invoice(renew.membership, invoice)
    return invoice

def pay_invoice(invoice):
    membership = invoice.membership
    invoice.status = "paid"
    invoice.payment_date = timezone.now()
    generate_invoice(membership, invoice)
    membership_payment_manager(membership, invoice)

def pending_invoice(invoice):
    membership = invoice.membership
    renew = invoice.renewal_period
    generate_invoice(membership, invoice)
    renew.active = True
    renew.encobro = True
    renew.save()