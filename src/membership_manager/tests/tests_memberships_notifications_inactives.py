from async_notifications.models import EmailNotification
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from membership_manager.models import Invoice, Membership
from membership_manager.task_utils import membership_deactivating
from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_deactivate


class MembershipExpirationInactiveNotify(TestCase):

    now = timezone.now()

    def setUp(self):
        create_contacts(2)
        add_organization()
        self.user = User.objects.create(username='admin',password='123456',email='admin@admin.com',
                                        is_superuser=True)
        self.memberships = generate_memberships_to_deactivate()

    def test_membership_expiration_notify(self):
        membership_deactivating(self.now)
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 3
        self.assertEqual(result, expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        emails_expected = 3
        self.assertEqual(check_emails, emails_expected)
        check_memb = Membership.objects.filter(state='inactive').count()
        memb_expected = 3
        self.assertEqual(check_memb, memb_expected)

        memb1 = self.memberships['membership_expired']['membership']
        memb2 = self.memberships['membership_graceperiod_active']['membership']
        memb3 = self.memberships['membership_expired_yesterday']['membership']
        memb4 = self.memberships['membership_expired_with_one_renewal']['membership']

        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()
        memb4.refresh_from_db()


        self.assertEqual(memb1.state, 'inactive')
        self.assertEqual(memb2.state, 'graceperiod')
        self.assertEqual(memb3.state, 'inactive')
        self.assertEqual(memb4.state, 'inactive')



# def test_membership_expiration_notify_secondtime(self):
#         membership_deactivating(self.now)
#         result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
#         expected = 1
#         memb_check = Membership.objects.filter(state='inactive').count()
#         self.assertEqual(memb_check, expected)
#         self.assertEqual(result, expected)
#         check_emails = EmailNotification.objects.filter(enqueued=True).count()
#         self.assertEqual(check_emails, expected)
#
#         membership_deactivating(self.now)
#         result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
#         expected = 1
#         memb_check = Membership.objects.filter(state='inactive').count()
#         self.assertEqual(memb_check, expected)
#         self.assertEqual(result, expected)
#         check_emails = EmailNotification.objects.filter(enqueued=True).count()
#         self.assertEqual(check_emails, expected)