from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.utils import timezone

from membership_manager.admin_pdf import pay_invoice
from membership_manager.models import Invoice, Membership, MembershipRenew
from membership_manager.task_utils import membership_deactivating, renew_graceperiod, invoice_creation
from membership_manager.tests.utils import create_contacts, add_organization, generate_graceperiod_memberships

# Create your tests here.
from membership_manager.utils import loademailtemplates


class MembershipsGracePeriod(TestCase):
    now = timezone.now()
    def setUp(self):
        create_contacts(2)
        add_organization()
        generate_graceperiod_memberships()
        self.user = user = User.objects.create(username='myadmin',email='test@admin.com',password='123456',first_name='Administrator',last_name='GM',is_superuser=True)

    def test_membership_graceperiod_deactivate(self):
        membership_deactivating(self.now)
        mem_check = Membership.objects.filter(state='inactive').count()
        mem_expected = 2
        mem_renews_check = MembershipRenew.objects.filter(active=False,membership__state='inactive').count()
        mem_renews_expected = 4
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 2
        self.assertEqual(result,expected)
        self.assertEqual(mem_check,mem_expected)
        self.assertEqual(mem_renews_check,mem_renews_expected)

    # def test_membership_invoice_creation(self):
    #     invoice_creation(self.now)
    #     result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
    #     expected = 0
    #     self.assertEqual(result, expected)
    #
    # def test_membership_renew_graceperiod(self):
    #     renew_graceperiod(self.now)
    #     result = LogEntry.objects.filter(object_repr='Membresia ha cambiado a periodo de prueba').count()
    #     expected = 1
    #     self.assertEqual(result,expected)
    #
    # def test_membership_payment(self):
    #     request = self.factory.post('/admin/membership_manager/invoice/',data={})
    #     request.user = self.user
    #     pay_invoice(object,request,self.invoices)
    #     check_inv = Invoice.objects.filter(status = 'paid').count()
    #     inv_expected = 2
    #     check_logs = LogEntry.objects.filter(object_repr='Pago de membresía realizado, poniendo todos los periódos de gracia inactivos').count()
    #     logs_expected = 2
    #     self.assertEqual(check_inv,inv_expected)
    #     self.assertEqual(check_logs,logs_expected)