from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.timezone import now
from django.test import TestCase
from django_countries.fields import Country
from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import Membership, Organization, MembershipRenew, Invoice


class MembershipDeactivatingTestCase(TestCase):

    fixtures = ['async_notifications_email_template.json', 'async_notifications_template_context.json',
                'membership_core.json']

    def setUp(self):
        self.username = 'user'
        self.password = 'password'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)
        self.now = now()

        self.organization1 = Organization.objects.create(
            name="Orga",
            email="org@gmail.com",
            country=Country(code='CR'),
            active=True
        )

        self.membership1 = Membership.objects.create(
            creation_date=now(),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.last(),
            organization=self.organization1
        )


    def test_membership_deactivating_base(self):

        data = {'action': 'membership_deactivating_membership',
                '_selected_action': [self.membership1.pk, ]}
        change_url = reverse('admin:membership_manager_membership_changelist')
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(change_url, data, follow=True)
        self.client.logout()

        self.assertEqual(response.status_code, 200)

        self.renew = MembershipRenew.objects.filter(membership=self.membership1).first()
        self.invoice = Invoice.objects.filter(membership=self.membership1, renewal_period=self.renew)

        self.assertTrue(self.invoice is not None)










