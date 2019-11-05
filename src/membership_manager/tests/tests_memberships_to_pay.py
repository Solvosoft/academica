from async_notifications.models import EmailNotification
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

# Create your tests here.
from django.utils import timezone

from membership_manager.admin_pdf import pay_invoice
from membership_manager.models import Invoice
from membership_manager.task_utils import membership_deactivating, renew_graceperiod, invoice_creation
from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_pay
from membership_manager.utils import loademailtemplates


class MembershipToPay(TestCase):
    now = timezone.now()

    def setUp(self):
        self.factory = RequestFactory()
        create_contacts(2)
        add_organization()
        generate_memberships_to_pay()
        self.invoices = Invoice.objects.all()

    def test_membership_renew_graceperiod(self):
        renew_graceperiod(self.now)
        result = LogEntry.objects.filter(object_repr='Membresia ha cambiado a periodo de prueba').count()
        expected = 0
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(check_emails, expected)
        self.assertEqual(result,expected)

    def test_membership_invoice_creation(self):
        invoice_creation(self.now)
        result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
        expected = 0
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(check_emails, expected)
        self.assertEqual(result, expected)

    def test_membership_graceperiod_deactivate(self):
        membership_deactivating(self.now)
        result = LogEntry.objects.filter(object_repr='Membresía inactiva por falta de pago').count()
        expected = 0
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(check_emails,expected)
        self.assertEqual(result,expected)

    def test_membership_payment(self):
        request = self.factory.post('/admin/membership_manager/invoice/',data={})
        user = User.objects.create(username='myadmin',email='test@admin.com',password='123456',first_name='Administrator',last_name='GM')
        request.user = user
        expected = 4
        pay_invoice(object,request,self.invoices)
        result = LogEntry.objects.filter(object_repr='Pago de membresía realizado, poniendo todos los periódos de gracia inactivos').count()
        response = Invoice.objects.filter(status='paid').count()
        self.assertEqual(response,expected)
        self.assertEqual(result,expected)
        check_emails = EmailNotification.objects.filter(subject='Pago de membresía - Código Sur').count()
        self.assertEqual(check_emails,expected)
