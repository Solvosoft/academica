from django.utils.timezone import now
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from dateutil.relativedelta import relativedelta
from django_countries.fields import Country

from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import Invoice, Membership, MembershipRenew, Contact, Organization


class SendWelcomeNotificationTestCase(TestCase):

    fixtures = ['async_notifications_email_template.json', 'async_notifications_template_context.json',
                'membership_core.json']

    def setUp(self):
        self.username = 'user'
        self.password = 'password'
        self.user = User.objects.create_superuser(self.username, 'test@example.com', self.password)
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

        self.records = 1

        while self.records < 9:
            membership_pk = Membership.objects.all()[self.records-1].pk

            action = {'action': 'send_welcome_notification',
                    '_selected_action': [membership_pk, ]}

            change_url = reverse('admin:membership_manager_membership_changelist')
            self.client.login(username=self.username, password=self.password)
            response = self.client.post(change_url, action, follow=True)
            self.client.logout()

            self.assertEqual(response.status_code, 200)

            self.records += 1






