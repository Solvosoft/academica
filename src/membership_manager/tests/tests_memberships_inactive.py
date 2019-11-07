from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

# Create your tests here.
from django.utils import timezone

from membership_manager.admin_pdf import pay_invoice
from membership_manager.models import Invoice, Membership
from membership_manager.task_utils import membership_deactivating, renew_graceperiod, invoice_creation
from membership_manager.tests.utils import create_contacts, add_organization, generate_inactive_memberships
from membership_manager.utils import loademailtemplates


class MembershipsInactive(TestCase):
    """Testing property fucntionality of tasks when We have inactive membership cases.
             Description:
              This methid is in charge of check if systems works property.
              All of this tests was coded only for inactive membership case.

              Attributes:
               now (date): Holds the timezone.now() ("TODAYs,DATETIME").
               factory (:obj:`RequestFactory`) Needed to make a request , on payment test..
               invoices (:queryset:`Invoices`) used like param..

              Extra:
                  Also there is the use of 3 vital functions,
                      - create_contacts() #contacts.
                      - add_organization() #organizations related with contacts
                      - generate_memberships_to_pay() # Create the scenario.
          """
    now = timezone.now()
    def setUp(self):
        self.factory = RequestFactory()
        create_contacts(2)
        add_organization()
        generate_inactive_memberships()
        self.invoices= Invoice.objects.filter(status='pending')
        self.user = user = User.objects.create(username='myadmin',email='test@admin.com',password='123456',first_name='Administrator',last_name='GM',is_superuser=True)


    def test_membership_invoice_creation(self):
        invoice_creation(self.now)
        check_inv = Invoice.objects.filter(status = 'pending').count()
        inv_expected = 2
        result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
        expected = 0
        self.assertEqual(result, expected)
        self.assertEqual(check_inv, inv_expected)

    def test_membership_renew_graceperiod(self):

        renew_graceperiod(self.now)
        check_memb = Membership.objects.filter(state = 'graceperiod').count()
        memb_expected = 1
        result = LogEntry.objects.filter(object_repr='Membresia ha cambiado a periodo de prueba').count()
        expected = 0
        self.assertEqual(result,expected)
        self.assertEqual(check_memb,memb_expected)

    def test_membership_graceperiod_deactivate(self):
        membership_deactivating(self.now)
        check_memb = Membership.objects.filter(state='inactive').count()
        memb_expected = 3
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 1
        self.assertEqual(result,expected)
        self.assertEqual(check_memb,memb_expected)

    def test_membership_payment(self):
        request = self.factory.post('/admin/membership_manager/invoice/',data={})
        request.user = self.user
        pay_invoice(object,request,self.invoices)
        check_inv = Invoice.objects.filter(status = 'paid').count()
        inv_expected = 2
        check_logs = LogEntry.objects.filter(object_repr='Pago de membresía realizado, poniendo todos los periódos de gracia inactivos').count()
        logs_expected = 2
        self.assertEqual(check_inv,inv_expected)
        self.assertEqual(check_logs,logs_expected)

