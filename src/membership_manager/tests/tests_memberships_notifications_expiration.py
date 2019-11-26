from async_notifications.models import EmailNotification
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from membership_manager.models import Invoice, Membership
from membership_manager.task_utils import notify_invoice_expiration, invoice_creation
from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_notify_expiration



class MembershipExpirationNotify(TestCase):

    now = timezone.now()

    def setUp(self):
        """
            Case #0: Notificación membresías por vencer. Rango 0 - 60 días
             'membership_70_days_to_expire'
             'membership_60_days_to_expire'
             'membership_30_days_to_expire'
             'membership_15_days_to_expire'
             'membership_7_days_to_expire'
             'membership_1_day_to_expire'
        """
        create_contacts(2)
        add_organization()
        self.user = User.objects.create(username='admin',password='123456',email='admin@admin.com',
                                        is_superuser=True)
        self.memberships = generate_memberships_to_notify_expiration()

    def test_membership_expiration_notify(self):
        notify_invoice_expiration(self.now)
        result = LogEntry.objects.filter(object_repr='Notificación de pago pendiente enviada').count()
        expected = 4
        self.assertEqual(result,expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        emails = EmailNotification.objects.filter(enqueued=True)
        emails_expected = 4
        self.assertEqual(check_emails,emails_expected)
        check_memb = Membership.objects.filter(state='active').count()
        memb_expected = 6
        self.assertEqual(check_memb, memb_expected)

        memb1 = self.memberships['membership_70_days_to_expire']['membership']
        memb2 = self.memberships['membership_60_days_to_expire']['membership']
        memb3 = self.memberships['membership_30_days_to_expire']['membership']
        memb4 = self.memberships['membership_15_days_to_expire']['membership']
        memb5 = self.memberships['membership_7_days_to_expire']['membership']
        memb6 = self.memberships['membership_1_day_to_expire']['membership']
        memb7 = self.memberships['membership_expired_yesterday']['membership']
        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()
        memb4.refresh_from_db()
        memb5.refresh_from_db()
        memb6.refresh_from_db()
        memb7.refresh_from_db()

        self.assertEqual(memb1.state, 'active')
        self.assertEqual(memb2.state, 'active')
        self.assertEqual(memb3.state, 'active')
        self.assertEqual(memb4.state, 'active')
        self.assertEqual(memb5.state, 'active')
        self.assertEqual(memb6.state, 'active')
        self.assertEqual(memb7.state, 'graceperiod')

    def test_membership_expiration_notify_secondtime(self):
        notify_invoice_expiration(self.now)
        notify_invoice_expiration(self.now)
        result = LogEntry.objects.filter(object_repr='Notificación de pago pendiente enviada').count()
        expected = 8
        self.assertEqual(result, expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        emails_expected = 8
        self.assertEqual(check_emails, emails_expected)
        check_memb = Membership.objects.filter(state='active').count()
        memb_expected = 6
        self.assertEqual(check_memb, memb_expected)

        memb1 = self.memberships['membership_70_days_to_expire']['membership']
        memb2 = self.memberships['membership_60_days_to_expire']['membership']
        memb3 = self.memberships['membership_30_days_to_expire']['membership']
        memb4 = self.memberships['membership_15_days_to_expire']['membership']
        memb5 = self.memberships['membership_7_days_to_expire']['membership']
        memb6 = self.memberships['membership_1_day_to_expire']['membership']
        memb7 = self.memberships['membership_expired_yesterday']['membership']
        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()
        memb4.refresh_from_db()
        memb5.refresh_from_db()
        memb6.refresh_from_db()
        memb7.refresh_from_db()

        self.assertEqual(memb1.state, 'active')
        self.assertEqual(memb2.state, 'active')
        self.assertEqual(memb3.state, 'active')
        self.assertEqual(memb4.state, 'active')
        self.assertEqual(memb5.state, 'active')
        self.assertEqual(memb6.state, 'active')
        self.assertEqual(memb7.state, 'graceperiod')
