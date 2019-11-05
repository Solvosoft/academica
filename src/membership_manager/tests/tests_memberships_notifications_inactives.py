# from async_notifications.models import EmailNotification
# from django.contrib.admin.models import LogEntry
# from django.contrib.auth.models import User
# from django.test import TestCase
#
# # Create your tests here.
# from django.utils import timezone
#
# from membership_manager.models import Invoice, Membership
# from membership_manager.task_utils import membership_deactivating
# from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_deactivate
#
#
# class MembershipExpirationNotify(TestCase):
#     now = timezone.now()
#
#     def setUp(self):
#         create_contacts(2)
#         add_organization()
#         generate_memberships_to_deactivate()
#         self.user = User.objects.create(username='admin',password='123456',email='admin@admin.com',
#                                         is_superuser=True)
#
#     def test_membership_expiration_notify(self):
#         membership_deactivating(self.now)
#         result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
#         expected = 1
#         memb_check = Membership.objects.filter(state='inactive').count()
#         self.assertEqual(memb_check, expected)
#         self.assertEqual(result, expected)
#         check_emails = EmailNotification.objects.filter(enqueued=True).count()
#         self.assertEqual(check_emails, expected)