from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase

# last_renew_start_date
from django.utils.timezone import now
from django_countries.fields import Country

from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import MembershipRenew, Membership, Organization
from membership_manager.task_utils import invoice_creation


class RenewStartDateTestCase(TestCase):
    """
    Escenario:


    """
    fixtures = ['async_notifications_email_template.json', 'async_notifications_template_context.json', 'membership_core.json']

    def setUp(self):
        self.now = now()
        self.organization = Organization.objects.create(
            name="Orga",
            email="org@gmail.com",
            country=Country(code='CR'),
            active=True
        )

        self.membership = Membership.objects.create(
            creation_date=now(),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.first(),
            organization=self.organization
        )

        self.username = 'user'
        self.password = 'password'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)

    # last_renew_start_date
    def test_lrsd_base(self):
        """
        Caso base, debe seleccionarse la segunda por estar posterior en el tiempo
        """
        MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = self.now+relativedelta(months=-12),
            end_date = self.now+relativedelta(days=+60),
            encobro = False,
            active = True,
        )
        meminv=MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = self.now+relativedelta(days=+60),
            end_date = self.now+relativedelta(months=+12),
            encobro = True,
            active = True,
        )

        total, invoicestxt = invoice_creation(self.now)
        self.assertEqual(total, 1)