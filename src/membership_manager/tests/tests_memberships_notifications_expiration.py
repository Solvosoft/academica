# from async_notifications.models import EmailNotification
# from django.contrib.admin.models import LogEntry
# from django.contrib.auth.models import User
# from django.test import TestCase
#
# # Create your tests here.
# from django.utils import timezone
#
# from membership_manager.models import Invoice
# from membership_manager.task_utils import notify_invoice_expiration
# from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_notify_expiration
#
#
#
# class MembershipExpirationNotify(TestCase):
#     now = timezone.now()
#
#     def setUp(self):
#         create_contacts(2)
#         add_organization()
#         generate_memberships_to_notify_expiration()
#         self.user = User.objects.create(username='admin',password='123456',email='admin@admin.com',
#                                         is_superuser=True)
#
#     def test_membership_expiration_notify(self):
#         notify_invoice_expiration(self.now)
#         result = LogEntry.objects.filter(object_repr='Notificación de pago pendiente enviada').count()
#         expected = 4
#
#         check_invoice_result = Invoice.objects.all().count()
#         check_emails = EmailNotification.objects.filter(enqueued=True).count()
#
#         self.assertEqual(result, expected)
#         self.assertEqual(check_emails, 4)
#         self.assertEqual(check_invoice_result, expected)
#
