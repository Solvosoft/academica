from async_notifications.models import EmailNotification
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.
from django.utils import timezone

from membership_manager.models import Invoice, Membership
from membership_manager.task_utils import membership_deactivating
from membership_manager.tests.utils import create_contacts, add_organization, generate_memberships_to_deactivate


class MembershipExpirationInactiveNotify(TestCase):
    """Testing email notifications and logs onmembership deactivating.
         Description:
          This methid is in charge of check if the emails was enqueued and systems works property.
          All of this tests was coded only for membership deactivating cases.

         Attributes:
             now (date): Holds the timezone.now() ("TODAYs,DATETIME").
             user (:obj:`User`) for the log we need an superuser

          Extra:
              Also there is the use of 3 vital functions,
                  - create_contacts() #contacts.
                  - add_organization() #organizations related with contacts
                  - generate_memberships_to_pay() # Create the scenario.
      """
    now = timezone.now()

    def setUp(self):
        create_contacts(2)
        add_organization()
        generate_memberships_to_deactivate()
        self.user = User.objects.create(username='admin',password='123456',email='admin@admin.com',
                                        is_superuser=True)

    def test_membership_expiration_notify(self):
        membership_deactivating(self.now)
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 1
        memb_check = Membership.objects.filter(state='inactive').count()
        self.assertEqual(memb_check, expected)
        self.assertEqual(result, expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(check_emails, expected)

    def test_membership_expiration_notify_secondtime(self):
        membership_deactivating(self.now)
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 1
        memb_check = Membership.objects.filter(state='inactive').count()
        self.assertEqual(memb_check, expected)
        self.assertEqual(result, expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(check_emails, expected)

        membership_deactivating(self.now)
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 1
        memb_check = Membership.objects.filter(state='inactive').count()
        self.assertEqual(memb_check, expected)
        self.assertEqual(result, expected)
        check_emails = EmailNotification.objects.filter(enqueued=True).count()
        self.assertEqual(check_emails, expected)