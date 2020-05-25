from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase

# last_renew_start_date
from django.utils import timezone
from django_countries.fields import Country

from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import MembershipRenew, Membership, Organization
from membership_manager.task_utils import invoice_creation, generate_renew


class RenewStartDateTestCase(TestCase):
    fixtures = ['async_notifications_email_template.json', 'async_notifications_template_context.json', 'membership_core.json']

    def setUp(self):
        self.now = timezone.localdate(timezone.now())
        self.username = 'user'
        self.password = 'password'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)

        self.organization1 = Organization.objects.create(
            name="Orga",
            email="org@gmail.com",
            country=Country(code='CR'),
            active=True
        )
        self.membership = Membership.objects.create(
            creation_date=timezone.localtime(timezone.now()),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.filter(months=12).first(),
            organization = self.organization1
        )
        self.membership2 = Membership.objects.create(
            creation_date=timezone.localtime(timezone.now()),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.filter(months=12).first(),
            organization = self.organization1
        )

        self.membership_2months = Membership.objects.create(
            creation_date=timezone.localtime(timezone.now()),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.filter(months=2).first(),
            organization = self.organization1
        )

        self.membership_1months = Membership.objects.create(
            creation_date=timezone.localtime(timezone.now()),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.filter(months=1).first(),
            organization = self.organization1
        )

    # last_renew_start_date
    def test_lrsd_base(self):
        """
        Caso base, debe seleccionarse la segunda por estar posterior en el tiempo
        """
        ok_date = self.now
        MembershipRenew.objects.create(
            creation_date=timezone.localtime(timezone.now()),
            membership = self.membership,
            start_date = self.now+relativedelta(months=-12),
            end_date = self.now+relativedelta(days=+60),
            encobro = True,
            active = True,
        )
        MembershipRenew.objects.create(
            creation_date=timezone.localtime(timezone.now()),
            membership = self.membership2,
            start_date = self.now+relativedelta(months=-12),
            end_date = self.now,
            encobro = True,
            active = True,
        )

        invoice_creation(self.now)
        generate_renew(self.now)

        self.assertEqual(self.membership.renews.count(), 2)
        self.assertEqual(self.membership2.renews.count(), 1)


        # if run again, don't create  new renew
        invoice_creation(self.now)
        generate_renew(self.now)

        self.assertEqual(self.membership.renews.count(), 2)
        self.assertEqual(self.membership2.renews.count(), 1)

        # if run tomorrow do nothing
        invoice_creation(self.now + relativedelta(days=+1))
        generate_renew(self.now + relativedelta(days=+1))

        self.assertEqual(self.membership.renews.count(), 2)
        self.assertEqual(self.membership2.renews.count(), 1)

        # if run on 60 days do nothing
        invoice_creation(self.now + relativedelta(days=+60))
        generate_renew(self.now + relativedelta(days=+60))

        self.assertEqual(self.membership.renews.count(), 2)
        self.assertEqual(self.membership2.renews.count(), 1)



    def test_short_periods_1month(self):
        MembershipRenew.objects.create(
            creation_date=timezone.localtime(timezone.now()),
            membership = self.membership_1months,
            start_date = self.now,
            end_date = self.now+relativedelta(days=30),
            encobro = True,
            active = True,
        )

        # if run  create  new renew
        invoice_creation(self.now)
        generate_renew(self.now)
        self.assertEqual(self.membership_1months.renews.count(), 2)

        # if run tomorrow do nothing
        invoice_creation(self.now + relativedelta(days=+1))
        generate_renew(self.now + relativedelta(days=+1))
        self.assertEqual(self.membership_1months.renews.count(), 3)

        # if run on 60 days do nothing
        invoice_creation(self.now + relativedelta(days=+60))
        generate_renew(self.now + relativedelta(days=+60))

        self.assertEqual(self.membership_1months.renews.count(), 4)

    def test_short_periods_2months(self):

        MembershipRenew.objects.create(
            creation_date=timezone.localtime(timezone.now()),
            membership = self.membership_2months,
            start_date = self.now,
            end_date = self.now+relativedelta(days=60),
            encobro = True,
            active = True,
        )

        # if run and create one
        invoice_creation(self.now)
        generate_renew(self.now)

        self.assertEqual(self.membership_2months.renews.count(), 2)

        # if run tomorrow do nothing
        invoice_creation(self.now + relativedelta(days=+1))
        generate_renew(self.now + relativedelta(days=+1))


        self.assertEqual(self.membership_2months.renews.count(), 2)

        # if run on 60 days create new
        invoice_creation(self.now + relativedelta(days=+60))
        generate_renew(self.now + relativedelta(days=+60))


        self.assertEqual(self.membership_2months.renews.count(), 2)
