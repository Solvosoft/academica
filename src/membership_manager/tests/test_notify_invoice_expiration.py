from async_notifications.models import EmailNotification
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import Organization, Membership, MembershipRenew, Invoice
from django_countries.fields import Country

from membership_manager.task_utils import invoice_creation, generate_renew, notify_invoice_expiration
from membership_manager.utils import invoice_expiration_filter_queryset


class TestNotifyInvoiceExpiration(TestCase):

    fixtures = ['async_notifications_email_template.json', 'async_notifications_template_context.json', 'membership_core.json']

    def setUp(self):
        self.now = timezone.localdate(timezone.now())
        self.username = 'user'
        self.password = 'password'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)

        self.organization = Organization.objects.create(
            name="Orga",
            email="org@gmail.com",
            country=Country(code='CR'),
            active=True
        )
        self.membership1 = Membership.objects.create(
            creation_date=self.now+relativedelta(months=-6),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.filter(months=6).first(),
            organization = self.organization
        )

        self.renew1 = MembershipRenew.objects.create(
            creation_date=timezone.localtime(timezone.now())+relativedelta(months=-6),
            membership = self.membership1,
            start_date = self.now+relativedelta(months=-6),
            end_date = self.now+relativedelta(months=+6),
            encobro = True,
            active = True,
        )

        self.invoice1 = Invoice.objects.create(
            creation_date=self.renew1.end_date+relativedelta(days=-60),
            expiration_date=self.renew1.end_date+relativedelta(days=+60),
            status="pending",
            amount=120.0,
            membership=self.membership1,
            renewal_period=self.renew1,
            currency=SystemCurrency.objects.first()
        )

        self.membership2 = Membership.objects.create(
            creation_date=self.now+relativedelta(months=-3)+relativedelta(days=-2),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.filter(months=3).first(),
            organization = self.organization
        )

        self.renew2 = MembershipRenew.objects.create(
            creation_date=timezone.localtime(timezone.now())+relativedelta(months=-3)+relativedelta(days=-2),
            membership = self.membership2,
            start_date = self.membership2.creation_date+relativedelta(days=-2),
            end_date = self.now+relativedelta(months=+3)+relativedelta(days=-2),
            encobro = True,
            active = True,
        )

        self.invoice2 = Invoice.objects.create(
            creation_date=self.renew2.end_date+relativedelta(days=-60),
            expiration_date=self.renew2.end_date+relativedelta(days=+60),
            status="pending",
            amount=120.0,
            membership=self.membership2,
            renewal_period=self.renew2,
            currency=SystemCurrency.objects.first()
        )

        self.membership3 = Membership.objects.create(
            creation_date=self.now+relativedelta(months=-1),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.filter(months=1).first(),
            organization = self.organization
        )

        self.renew3 = MembershipRenew.objects.create(
            creation_date=timezone.localtime(timezone.now())+relativedelta(months=-1),
            membership = self.membership3,
            start_date = self.now+relativedelta(months=-1),
            end_date = self.now+relativedelta(months=+1),
            encobro = True,
            active = True,
        )

        self.invoice3 = Invoice.objects.create(
            creation_date=self.renew3.end_date+relativedelta(days=-60),
            expiration_date=self.renew3.end_date+relativedelta(days=+60),
            status="pending",
            amount=120.0,
            membership=self.membership3,
            renewal_period=self.renew3,
            currency=SystemCurrency.objects.first()
        )

    def test_invoice_expiration_filter_queryset(self):

        """
       En esta prueba se encuentra 1 sola factura dentro del rango de vencimiento
       """

        self.assertEqual(invoice_expiration_filter_queryset(self.now).count(), 1)

        """
        En esta prueba hay una sola factura dentro del rango [45, 30, 15, 7, 3, 2, 1] no importa si se ejecuta consecutivamente
        """

        self.assertEqual(invoice_expiration_filter_queryset(self.now).count(), 1)


    def test_notifity_invoice_expiration(self):

        """
        La siguiente función recibe el queryset de las facturas prontas a vencer y envía las notificaciones de vencimiento
        """

        notify_invoice_expiration(self.now)

        email = EmailNotification.objects.filter(message__contains="Orga").first()

        self.assertIsNotNone(email, msg="Se envio el email a la única factura pronta a vencer dentro del rango establecido")













