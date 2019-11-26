from async_notifications.models import EmailNotification
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from membership_manager.models import Invoice, Membership
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
        self.memberships = generate_memberships_to_notify_expiration_create_invoice()
        self.user = User.objects.create(username='admin',password='123456',email='admin@admin.com',
                                        is_superuser=True)

    def test_membership_invoice_creation_expiration_renew(self):
        """
        membership_invoice_create_110days
        membership_invoice_create_60days,
        membership_invoice_create_30days,
        membership_invoice_create_30days_with_invoice,
        membership_invoice_create_expired_without_invoice,
        :return:
        """
        invoice_creation(self.now)
        result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
        expected = 3
        self.assertEqual(result, expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        emails_expected = 3
        self.assertEqual(check_emails, emails_expected)
        check_memb = Membership.objects.filter(state='active').count()
        memb_expected = 5
        self.assertEqual(check_memb, memb_expected)
        check_inv = Invoice.objects.filter(status='pending', creation_date=self.now).count()
        inv_expected = 3
        self.assertEqual(check_inv, inv_expected)

        memb1 = self.memberships['membership_invoice_create_110days']['membership']
        memb2 = self.memberships['membership_invoice_create_60days']['membership']
        memb3 = self.memberships['membership_invoice_create_30days']['membership']
        memb4 = self.memberships['membership_invoice_create_30days_with_invoice']['membership']
        memb5 = self.memberships['membership_invoice_create_expired_without_invoice']['membership']

        ren1 = self.memberships['membership_invoice_create_110days']['renew']
        ren2 = self.memberships['membership_invoice_create_60days']['renew']
        ren3 = self.memberships['membership_invoice_create_30days']['renew']
        ren4 = self.memberships['membership_invoice_create_30days_with_invoice']['renew']
        ren5 = self.memberships['membership_invoice_create_expired_without_invoice']['renew']

        ren1.refresh_from_db()
        ren2.refresh_from_db()
        ren3.refresh_from_db()
        ren4.refresh_from_db()
        ren5.refresh_from_db()

        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()
        memb4.refresh_from_db()
        memb5.refresh_from_db()

        inv1 = self.memberships['membership_invoice_create_30days_with_invoice']['invoice']
        inv1.refresh_from_db()
        self.assertEqual(inv1.status, 'pending')
        self.assertEqual(memb1.state, 'active')
        self.assertEqual(memb2.state, 'active')
        self.assertEqual(memb3.state, 'active')
        self.assertEqual(memb4.state, 'active')
        self.assertEqual(memb5.state, 'active')
        self.assertTrue(ren1.active)
        self.assertTrue(ren2.active)
        self.assertTrue(ren3.active)
        self.assertTrue(ren4.active)
        self.assertTrue(ren5.active)
        self.assertFalse(ren1.graceperiod)
        self.assertFalse(ren2.graceperiod)
        self.assertFalse(ren3.graceperiod)
        self.assertFalse(ren4.graceperiod)
        self.assertFalse(ren5.graceperiod)

    # def test_membership_invoice_creation_expiration_renew_secondtime(self):
    #     #first time invoice_creation called
    #     invoice_creation(self.now)
    #     result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
    #     expected = 2
    #     check_invoice_result = Invoice.objects.all().count()
    #     self.assertEqual(result, expected)
    #     self.assertEqual(check_invoice_result, expected)
    #     check_emails = EmailNotification.objects.filter(enqueued=True).count()
    #     self.assertEqual(check_emails, 2)
    #
    #     #second time invoice_creation called
    #
    #     invoice_creation(self.now)
    #     result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
    #     expected = 2
    #     check_invoice_result = Invoice.objects.all().count()
    #     self.assertEqual(result, expected) #STILL 2 LogEntries.
    #     self.assertEqual(check_invoice_result, expected)
    #     check_emails = EmailNotification.objects.filter(enqueued=True).count()
    #     self.assertEqual(check_emails, 2)



