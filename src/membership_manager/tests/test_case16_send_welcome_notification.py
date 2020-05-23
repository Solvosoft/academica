from async_notifications.models import EmailNotification
from django.utils.timezone import now
from django.test import TestCase
from django_countries.fields import Country
from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import Membership, Contact, Organization

class SendWelcomeNotificationTestCase(TestCase):

    fixtures = ['async_notifications_email_template.json', 'async_notifications_template_context.json',
                'membership_core.json']

    def setUp(self):
        self.now = now()
        self.count = 1
        self.state = True
        self.state_membership = "active"

        self.combination_state_list = [["active", True], ["inactive", False], ["active", False], ["inactive", True]]

        while self.count < 5:

            self.organization1 = Organization.objects.create(
                name="Orga"+str(self.count),
                email="org"+str(self.count)+"@gmail.com",
                country=Country(code='CR'),
                active=self.combination_state_list[self.count-1][1]
            )

            self.membership1 = Membership.objects.create(
                creation_date=now(),
                membership_type="Personal",
                annual_cost=120,
                currency=SystemCurrency.objects.first(),
                state=self.combination_state_list[self.count-1][0],
                renewal_period=RenewalPeriod.objects.first(),
                organization=self.organization1
            )

            self.contact1 = Contact.objects.create(
                first_name="contact"+str(self.count),
                last_name="contact"+str(self.count),
                email="contact"+str(self.count)+"@gmail.com",
                country=Country(code='MX'),
                active=self.combination_state_list[self.count-1][1],
            )

            self.membership2 = Membership.objects.create(
                creation_date=now(),
                membership_type="Personal",
                annual_cost=120,
                currency=SystemCurrency.objects.first(),
                state=self.combination_state_list[self.count-1][0],
                renewal_period=RenewalPeriod.objects.first(),
                contact=self.contact1
            )

            self.count+=1

    def test_send_welcome_email_base(self):

        email1 = EmailNotification.objects.filter(message__contains="Orga1")[0]
        email2 = EmailNotification.objects.filter(message__contains="Orga2")[0]
        email3 = EmailNotification.objects.filter(message__contains="Orga3")[0]
        email4 = EmailNotification.objects.filter(message__contains="Orga4")[0]
        email5 = EmailNotification.objects.filter(message__contains="contact1 contact1")[0]
        email6 = EmailNotification.objects.filter(message__contains="contact2 contact2")[0]
        email7 = EmailNotification.objects.filter(message__contains="contact3 contact3")[0]
        email8 = EmailNotification.objects.filter(message__contains="contact4 contact4")[0]

        """
        Se espera que el email1 y el email5 pasen la prueba porque son los únicos que tiene una organización
         o contacto activo y una membresía activa
        """

        self.assertTrue(email1 is not None)
        self.assertTrue(email5 is not None)

        """
        Se espera que el resto de los siguientes emails sean nulos.
        """

        self.assertFalse(email2 is not None)
        self.assertFalse(email3 is not None)
        self.assertFalse(email4 is not None)
        self.assertFalse(email6 is not None)
        self.assertFalse(email7 is not None)
        self.assertFalse(email8 is not None)










