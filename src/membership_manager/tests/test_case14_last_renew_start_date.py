from django.utils.timezone import now
from django.test import TestCase
from django_countries.fields import Country
from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import Membership, Organization, MembershipRenew, Invoice
from membership_manager.task_utils import update_last_daterenew


class LastRenewStartDateTestCase(TestCase):

    fixtures = ['async_notifications_email_template.json', 'async_notifications_template_context.json',
                'membership_core.json']

    def setUp(self):
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


    def test_last_renew_start_date_base(self):

        update_last_daterenew()
        self.assertTrue(self.membership1.last_renew_start_date==self.membership1.last_renew)










