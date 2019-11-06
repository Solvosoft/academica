from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from membership_manager.models import Membership, Invoice, MembershipRenew
from membership_manager.task_utils import membership_deactivating, renew_graceperiod, invoice_creation
from membership_manager.tests.utils import create_contacts, add_organization, generate_active_memberships_to_graceperiod
from membership_manager.utils import loademailtemplates
# Create your tests here.


class MembershipToPay(TestCase):
    now = timezone.now()
    def setUp(self):
        create_contacts(2)
        add_organization()
        generate_active_memberships_to_graceperiod()
        self.user = User.objects.create(username='admin', password='123456', email='admin@admin.com',
                                        is_superuser=True)

    def test_membership_graceperiod_deactivate(self):
        membership_deactivating(self.now)
        check_memb = Membership.objects.filter(state='inactive').count()
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 0
        self.assertEqual(result,expected)
        self.assertEqual(check_memb,expected)

    def test_membership_invoice_creation(self):
        invoice_creation(self.now)
        check_inv = Invoice.objects.all().count()
        result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
        expected = 1
        self.assertEqual(result, expected)
        self.assertEqual(check_inv, 3)

    def test_membership_renew_graceperiod(self):
        renew_graceperiod(self.now)
        check_memb = Membership.objects.filter(state='graceperiod').count()
        result = LogEntry.objects.all().count()
        expected = 1
        self.assertEqual(result,expected)
        self.assertEqual(check_memb,expected)


