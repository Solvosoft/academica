# from async_notifications.models import EmailNotification
# from django.contrib.admin.models import LogEntry
# from django.contrib.auth.models import User
# from django.test import TestCase
#
# # Create your tests here.
# from django.utils import timezone
#
# from membership_manager.models import Invoice
# from membership_manager.task_utils import invoice_creation
# from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_notify_expiration_create_invoice
# from membership_manager.utils import loademailtemplates
#
#
# class MembershipNotifications(TestCase):
#     now = timezone.now()
#     @classmethod
#     def setUpClass(cls):
#         super(MembershipNotifications, cls).setUpClass()
#         loademailtemplates()
#
#     def setUp(self):
#         create_contacts(2)
#         add_organization()
#         generate_memberships_to_notify_expiration_create_invoice()
#         self.user = User.objects.create(username='admin',password='123456',email='admin@admin.com',
#                                         is_superuser=True)
#
#     def test_membership_invoice_creation_expiration_renew(self):
#         invoice_creation(self.now)
#         result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
#         expected = 2
#         check_invoice_result = Invoice.objects.all().count()
#         check_emails = EmailNotification.objects.all().count()
#         self.assertEqual(result, expected)
#         self.assertEqual(check_emails, 5)
#         self.assertEqual(check_invoice_result, expected)
#
