from async_notifications.models import EmailNotification
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from membership_manager.models import Invoice
from membership_manager.task_utils import invoice_creation
from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_notify_expiration_create_invoice
from membership_manager.utils import loademailtemplates


class MembershipNotifyInvoiceCreation(TestCase):
    """Testing email notifications and logs on payment invoice_creation.
        Description:
         This methid is in charge of check if the emails was enqueued and systems works property.
         All of this tests was coded only for invoice creation cases.

        Attributes:
            now (date): Holds the timezone.now() ("TODAYs,DATETIME").
            user (:obj:`User`) for the log we need an superuser

         Extra:
             Also there is the use of 3 vital functions,
                 - create_contacts() #contacts.
                 - add_organization() #organizations related with contacts
                 - generate_memberships_to_pay() # Create the scenario.
     """
    now = timezone.now()

    def setUp(self):
        create_contacts(2)
        add_organization()
        generate_memberships_to_notify_expiration_create_invoice()
        self.user = User.objects.create(username='admin',password='123456',email='admin@admin.com',
                                        is_superuser=True)

    def test_membership_invoice_creation_expiration_renew(self):
        invoice_creation(self.now)
        result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
        expected = 2
        check_invoice_result = Invoice.objects.all().count()
        self.assertEqual(result, expected)
        self.assertEqual(check_invoice_result, expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(check_emails, 2)

    def test_membership_invoice_creation_expiration_renew_secondtime(self):
        #first time invoice_creation called
        invoice_creation(self.now)
        result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
        expected = 2
        check_invoice_result = Invoice.objects.all().count()
        self.assertEqual(result, expected)
        self.assertEqual(check_invoice_result, expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(check_emails, 2)

        #second time invoice_creation called

        invoice_creation(self.now)
        result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
        expected = 2
        check_invoice_result = Invoice.objects.all().count()
        self.assertEqual(result, expected) #STILL 2 LogEntries.
        self.assertEqual(check_invoice_result, expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(check_emails, 2)



