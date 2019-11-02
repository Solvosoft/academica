# from django.contrib.admin.models import LogEntry
# from django.test import TestCase
# from django.utils import timezone
# from membership_manager.task_utils import membership_deactivating, renew_graceperiod, invoice_creation
# from membership_manager.tests.tests_utils import create_contacts, add_organization, generate_active_memberships_to_graceperiod
# from membership_manager.utils import loademailtemplates
# # Create your tests here.
#
#
# class MembershipToPay(TestCase):
#     now = timezone.now()
#     def setUp(self):
#         loademailtemplates()
#         create_contacts(2)
#         add_organization()
#         generate_active_memberships_to_graceperiod()
#
#     def test_membership_graceperiod_deactivate(self):
#         membership_deactivating(self.now)
#         result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
#         expected = 0
#         self.assertEqual(result,expected)
#
#     def test_membership_invoice_creation(self):
#         invoice_creation(self.now)
#         result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
#         expected = 1
#         self.assertEqual(result, expected)
#
#     def test_membership_renew_graceperiod(self):
#         renew_graceperiod(self.now)
#         result = LogEntry.objects.filter(object_repr='Membresia ha cambiado a periodo de prueba').count()
#         expected = 1
#         self.assertEqual(result,expected)
#
#
