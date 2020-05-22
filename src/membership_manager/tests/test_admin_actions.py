from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now


from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import MembershipRenew, Membership, Invoice
from dateutil.relativedelta import relativedelta
from django.test import TestCase

class PayinvoiceactionTestCase(TestCase):
    fixtures = ['async_notifications_email_template.json', 'async_notifications_template_context.json',
                'membership_core.json']
    def setUp(self):
        self.username = 'user'
        self.password = 'password'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)
        self.now = now()
        self.membership = Membership.objects.create(
            creation_date=now(),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.first()
        )

        self.renew = MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = self.now+relativedelta(months=-1),
            end_date = self.now+relativedelta(months=+1),
            encobro = True,
            active = True,
        )

        self.invoice = Invoice.objects.create(
            creation_date=now(),
            expiration_date =self.now,
            membership = self.membership,
            renewal_period = self.renew,
            description ="test",
            amount = 1,
            currency =SystemCurrency.objects.first(),
            status = 'pending',
       )

    def test_payinvoiceaction_base(self):

        data = {'action': 'pay_invoice_action',
                '_selected_action': [self.invoice.pk, ]}
        change_url = reverse('admin:membership_manager_invoice_changelist')
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()

        self.assertEqual(response.status_code, 200)
        data = MembershipRenew.objects.filter(pk=self.renew.pk).values_list('encobro', 'active')

        self.assertFalse(data[0][0])
        self.assertTrue(data[0][1])