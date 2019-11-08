from async_notifications.models import EmailNotification
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

# Create your tests here.
from django.utils import timezone

from membership_manager.admin_pdf import pay_invoice
from membership_manager.models import Invoice, Membership, MembershipRenew
from membership_manager.task_utils import membership_deactivating, renew_graceperiod, invoice_creation
from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_pay
from membership_manager.utils import loademailtemplates


class MembershipNotifyPayment(TestCase):
    """Testing email notifications and logs on payment requests.
       Description:
        This methid is in charge of check if the emails was enqueued and systems works property.
        All of this tests was coded only for payment cases.

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
        self.user = User.objects.create(username='myadmin', email='test@admin.com', password='123456',
                                   first_name='Administrator', last_name='GM')
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
        request.user = self.user
        expected = 5
        pay_invoice(object,request,Invoice.objects.all())
        memb_check = Membership.objects.filter(state='active').count()
        memb_expected = 5
        memb_renews_check = MembershipRenew.objects.filter(active=True, creation_date__date=timezone.now().date()).count()
        memB_renews_expected = 4
        result = LogEntry.objects.filter(object_repr='Pago de membresía realizado, poniendo todos los periódos de gracia inactivos').count()
        response = Invoice.objects.filter(status='paid', payment_date=timezone.now().date()).count()
        check_emails = EmailNotification.objects.filter(subject='Pago de membresía - Código Sur').count()
        self.assertEqual(response,expected)
        self.assertEqual(result,expected)
        self.assertEqual(check_emails,expected)
        self.assertEqual(memb_check,memb_expected)
        self.assertEqual(memb_renews_check,memB_renews_expected)

    def test_membership_payment_secondtime(self):
        request = self.factory.post('/admin/membership_manager/invoice/',data={})
        request.user = self.user
        expected = 5
        #first time pay_invoice called
        pay_invoice(object,request,Invoice.objects.all())
        memb_check = Membership.objects.filter(state='active').count()
        memb_expected = 5 #At this point we have 5 active memberships from last test.
        memb_renews_check = MembershipRenew.objects.filter(active=True, creation_date__date=timezone.now().date()).count()
        memB_renews_expected = 4 #At this point we have 5 active memberships from last test.
        result = LogEntry.objects.filter(object_repr='Pago de membresía realizado, poniendo todos los periódos de gracia inactivos').count()
        response = Invoice.objects.filter(status='paid',payment_date=timezone.now().date()).count()
        self.assertEqual(response, expected)
        self.assertEqual(result,expected)
        check_emails = EmailNotification.objects.filter(subject='Pago de membresía - Código Sur').count()
        self.assertEqual(check_emails,expected)
        self.assertEqual(memb_check,memb_expected) # we have to change this after pay_invoice get fixed
        self.assertEqual(memb_renews_check,memB_renews_expected) # we have to change this after pay_invoice get fixed

        #second time pay_invoice called
        pay_invoice(object,request,Invoice.objects.all())
        response = Invoice.objects.filter(status='paid', payment_date=timezone.now().date()).count()
        expected = 5
        self.assertEqual(response, expected)
        memb_renews_check = MembershipRenew.objects.filter(active=True,
                                                           creation_date__date=timezone.now().date()).count()
        memB_renews_expected = 4  # At this point we see that there is any change when we use twice pay_invoice
        self.assertEqual(memb_renews_check, memB_renews_expected)
        result = LogEntry.objects.filter(
            object_repr='Pago de membresía realizado, poniendo todos los periódos de gracia inactivos').count()
        self.assertEqual(result,expected)
        check_emails = EmailNotification.objects.filter(subject='Pago de membresía - Código Sur').count()
        self.assertEqual(check_emails, expected)
