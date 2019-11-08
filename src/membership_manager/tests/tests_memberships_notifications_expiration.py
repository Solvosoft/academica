from async_notifications.models import EmailNotification
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from membership_manager.models import Invoice
from membership_manager.task_utils import notify_invoice_expiration, invoice_creation
from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_notify_expiration



class MembershipExpirationNotify(TestCase):
    """Testing email notifications and logs on membership expiration.
             Description:
              This method is in charge of check if the emails was enqueued and systems works property.
              All of this tests was coded only for membership expirations cases.

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
        generate_memberships_to_notify_expiration()
        self.user = User.objects.create(username='admin',password='123456',email='admin@admin.com',
                                        is_superuser=True)

    def test_membership_expiration_notify(self):
        notify_invoice_expiration(self.now)
        result = LogEntry.objects.filter(object_repr='Notificación de pago pendiente enviada').count()
        expected = 4
        check_invoice_result = Invoice.objects.all().count()
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(result, expected)
        self.assertEqual(check_emails, 4)
        self.assertEqual(check_invoice_result, expected)

    def test_membership_expiration_notify_secondtime(self):
        notify_invoice_expiration(self.now)
        result = LogEntry.objects.filter(object_repr='Notificación de pago pendiente enviada').count()
        expected = 4
        check_invoice_result = Invoice.objects.all().count()
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(result, expected)
        self.assertEqual(check_emails, 4)
        self.assertEqual(check_invoice_result, expected)

        notify_invoice_expiration(self.now)
        result = LogEntry.objects.filter(object_repr='Notificación de pago pendiente enviada').count()
        expected = 4
        check_invoice_result = Invoice.objects.all().count()
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(result, expected)
        self.assertEqual(check_emails, 4)
        self.assertEqual(check_invoice_result, expected)

