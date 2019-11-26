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
        self.memberships = generate_memberships_to_pay()
        self.invoices = Invoice.objects.all()

    def test_membership_payment(self):
        """
        membership_to_pay_graceperiod_expire_today,
        membership_to_pay_graceperiod_expired_inactive,
        membership_to_pay_active,
        membership_to_pay_inactive
        :return:
        """
        request = self.factory.post('/admin/membership_manager/invoice/',data={})
        request.user = self.user
        pay_invoice(object,request,Invoice.objects.all())
        result = LogEntry.objects.filter(object_repr='Pago de membresía realizado.').count()
        expected = 4
        self.assertEqual(result, expected)
        check_emails = EmailNotification.objects.filter(subject='Pago de membresía - Código Sur').count()
        emails_expected = 4
        self.assertEqual(check_emails, emails_expected)
        check_memb = Membership.objects.filter(state='active').count()
        memb_expected = 4
        self.assertEqual(check_memb, memb_expected)
        check_renews = MembershipRenew.objects.filter(active=True).count()
        renews_expected = 4
        self.assertEqual(check_renews, renews_expected)
        check_inv = Invoice.objects.filter(status='paid').count()
        inv_expected = 4
        self.assertEqual(check_inv, inv_expected)

        memb1 = self.memberships['membership_to_pay_graceperiod_expire_today']['membership']
        memb2 = self.memberships['membership_to_pay_graceperiod_expired_inactive']['membership']
        memb3 = self.memberships['membership_to_pay_active']['membership']
        memb4 = self.memberships['membership_to_pay_inactive']['membership']

        ren1 = self.memberships['membership_to_pay_graceperiod_expire_today']['renew']
        ren2 = self.memberships['membership_to_pay_graceperiod_expired_inactive']['renew']
        ren3 = self.memberships['membership_to_pay_active']['renew']
        ren4 = self.memberships['membership_to_pay_inactive']['renew']

        ren1.refresh_from_db()
        ren2.refresh_from_db()
        ren3.refresh_from_db()
        ren4.refresh_from_db()

        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()
        memb4.refresh_from_db()

        inv1 = self.memberships['membership_to_pay_graceperiod_expire_today']['invoice']
        inv2 = self.memberships['membership_to_pay_graceperiod_expired_inactive']['invoice']
        inv3 = self.memberships['membership_to_pay_active']['invoice']
        inv4 = self.memberships['membership_to_pay_inactive']['invoice']
        inv1.refresh_from_db()
        inv2.refresh_from_db()
        inv3.refresh_from_db()
        inv4.refresh_from_db()

        self.assertEqual(inv1.status, 'paid')
        self.assertEqual(inv2.status, 'paid')
        self.assertEqual(inv3.status, 'paid')
        self.assertEqual(inv4.status, 'paid')
        self.assertEqual(memb1.state, 'active')
        self.assertEqual(memb2.state, 'active')
        self.assertEqual(memb3.state, 'active')
        self.assertEqual(memb4.state, 'active')
        self.assertFalse(ren1.active)
        self.assertFalse(ren2.active)
        self.assertFalse(ren3.active)
        self.assertFalse(ren4.active)

