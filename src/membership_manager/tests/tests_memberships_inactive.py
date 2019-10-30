from django.contrib.admin.models import LogEntry
from django.test import TestCase, RequestFactory

# Create your tests here.
from django.utils import timezone

from membership_manager.admin_pdf import pay_invoice
from membership_manager.models import Invoice
from membership_manager.task_utils import membership_deactivating, renew_graceperiod, invoice_creation
from membership_manager.tests.tests_utils import create_contacts, add_organization, generate_graceperiod_memberships, \
    generate_active_memberships_to_graceperiod, generate_inactive_memberships, loadtemplates


class MembershipsInactive(TestCase):
    now = timezone.now()
    def setUp(self):
        self.factory = RequestFactory()
        loadtemplates()
        create_contacts(2)
        add_organization()
        generate_inactive_memberships()
        self.invoices= Invoice.objects.filter(status='pending')

    def test_membership_graceperiod_deactivate(self):
        membership_deactivating(self.now)
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 1
        self.assertEqual(result,expected)

    def test_membership_invoice_creation(self):
        invoice_creation(self.now)
        result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
        expected = 0
        self.assertEqual(result, expected)

    def test_membership_renew_graceperiod(self):
        renew_graceperiod(self.now)
        result = LogEntry.objects.filter(object_repr='Membresia ha cambiado a periodo de prueba').count()
        expected = 0
        self.assertEqual(result,expected)

    def test_membership_payment(self):
        request = self.factory.post('/admin/membership_manager/invoice/')
        pay_invoice(object,request,self.invoices)
        response = Invoice.objects.filter(status='paid').count()
        self.assertEqual(response,2)