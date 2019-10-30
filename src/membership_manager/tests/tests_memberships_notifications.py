# from django.test import TestCase
#
# # Create your tests here.
# from django.utils import timezone
#
# from membership_manager.task_utils import membership_deactivating, renew_graceperiod, invoice_creation
# from membership_manager.tests.tests_utils import create_contacts, add_organization, generate_graceperiod_memberships, \
#     generate_memberships_to_pay, loadtemplates
#
#
# class MembershipNotifications(TestCase):
#     now = timezone.now()
#     def setUp(self):
#         loadtemplates()
#         create_contacts(2)
#         add_organization()
#         generate_memberships_to_pay()
#
#     def test_membership_to_expire(self):
#         response = invoice_creation(self.now)
#         expected = 'Membresía inactiva por falta de pago'
#         self.assertEqual(response,expected)
#
