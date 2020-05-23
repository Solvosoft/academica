from django.utils.timezone import now
from django.test import TestCase
from django_countries.fields import Country
from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import Membership, Organization, Invoice
from membership_manager.renew_utils import create_renew
from membership_manager.task_utils import create_invoice_tool


class CreateInvoiceToolTestCase(TestCase):

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


    def test_create_invoice_tool_base(self):

        self.renew = create_renew(self.membership1)
        create_invoice_tool(self.renew.pk)
        self.invoice = Invoice.objects.get(renewal_period=self.renew)


        """
        Resultado esperado la función create_invoice_tool genera la factura en caso de que no exista y construye su pdf
        """
        self.assertTrue(self.invoice.pdf_invoice is not None)


        """
       Resultado contrario no se crea la factura ni el pdf
       """

        self.assertFalse(self.invoice.pdf_invoice is not None)










