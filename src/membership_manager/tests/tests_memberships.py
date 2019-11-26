from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from membership_manager.models import Membership, Invoice
from membership_manager.task_utils import membership_deactivating, renew_graceperiod, invoice_creation
from membership_manager.tests.utils import create_contacts, add_organization, \
    generate_membershib_to_inactive, generate_membership_to_graceperiod, \
    generate_membership_to_create_invoice
# Create your tests here.

class MembershipsRegular(TestCase):
    now = timezone.now()
    def setUp(self):
        """
    Case #0: Membresías en periodo de prueba , a ser desactivadas
    Case #1: Membresías activas, cambian a periodo de prueba
    Case #2: Membresías activas, para crear invoices
    Case #3: Membresías activas con inconsistencia en los datos:
        'membership_active_without_renewal'
    """
        create_contacts(2)
        add_organization()
        self.user = User.objects.create(username='admin', password='123456', email='admin@admin.com',
                                        is_superuser=True)

    def test_membership_graceperiod_deactivate(self):
        """
        This test create 3 membership with renewal period in grace_period with this characteristics:
        - 1 end today
        - 2 ended yesterday
        - 3 end tomorrow

        It's experected that 2 membership change his state to inactive
        """
        memberships = generate_membershib_to_inactive()
        membership_deactivating(self.now)
        check_memb = Membership.objects.filter(state='inactive').count()
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 2
        self.assertEqual(result,expected)
        self.assertEqual(check_memb,expected)

        memb1 = memberships[0]['membership']
        memb2 = memberships[1]['membership']
        memb3 = memberships[2]['membership']
        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()

        self.assertEqual(memb1.state,'inactive')
        self.assertEqual(memb2.state,'inactive')
        self.assertEqual(memb3.state,'graceperiod')

    def test_membership_graceperiod_activate(self):
        """
        This test create 3 membership with renewal period active with this characteristics:
        - 1 end today
        - 2 ended yesterday
        - 3 end tomorrow

        It's experected that 2 membership change his state to graceperiod,
        also is expected the creation of two more renewals on membership 1 and 2 with this characteristics:
            1 & 2 - graceperiod True, active True

        """
        memberships = generate_membership_to_graceperiod()
        renew_graceperiod(self.now)
        check_memb = Membership.objects.filter(state='graceperiod').count()
        result = LogEntry.objects.filter(object_repr='Membresia ha cambiado a periodo de prueba').count()
        expected = 2
        self.assertEqual(result, expected)
        self.assertEqual(check_memb, expected)

        memb1 = memberships[0]['membership']
        memb2 = memberships[1]['membership']
        memb3 = memberships[2]['membership']
        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()

        renew1 = memb1.renews.last()
        renew3 = memb3.renews.last()
        self.assertTrue(renew1.graceperiod)
        self.assertTrue(renew3.graceperiod)
        self.assertTrue(renew1.active)
        self.assertTrue(renew3.active)

        self.assertEqual(memb1.state, 'graceperiod')
        self.assertEqual(memb2.state, 'active')
        self.assertEqual(memb3.state, 'graceperiod')

    def test_membership_invoice_creation(self):
        """
        This test create 3 membership with renewal period active without invoices, with this characteristics:
        - 1 end today
        - 2 end 30 days
        - 3 end 30 days (this already have invoice)

        It's experected that 2 invoice may be created today,
        also is expected that we dont have any change on membership or renewal states.
        """
        memberships = generate_membership_to_create_invoice()
        invoice_creation(self.now)
        check_memb = Invoice.objects.filter(creation_date__date=timezone.localdate(self.now)).count()
        result = LogEntry.objects.filter(object_repr='Factura creada pendiente de pago').count()
        inv_expected = 3
        expected = 2
        self.assertEqual(result, expected)
        self.assertEqual(check_memb, inv_expected)

        memb1 = memberships[0]['membership']
        memb2 = memberships[1]['membership']
        memb3 = memberships[2]['membership']
        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()

        renew1 = memb1.renews.first()
        renew2 = memb2.renews.first()
        renew3 = memb3.renews.first()
        self.assertFalse(renew1.graceperiod)
        self.assertFalse(renew2.graceperiod)
        self.assertFalse(renew3.graceperiod)
        self.assertTrue(renew1.active,True)
        self.assertTrue(renew2.active,True)
        self.assertTrue(renew3.active,True)

        self.assertEqual(memb1.state, 'active')
        self.assertEqual(memb2.state, 'active')
        self.assertEqual(memb3.state, 'active')

