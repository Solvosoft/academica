from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase, RequestFactory
from django.utils import timezone

from membership_manager.models import Membership
from membership_manager.task_utils import membership_deactivating, renew_graceperiod
from membership_manager.tests.utils import create_contacts, add_organization, \
    generate_memberships_graceperiod_to_inactive_and_active_to_graceperiod


class MembershipsGracePeriod(TestCase):

    now = timezone.now()
    def setUp(self):
        """
            Case #0: Membresías en periodo de gracia vencido y por vencer hoy
                'membership_graceperiod_expired'
                'membership_graceperiod_expire_today'
                'membership_graceperiod_incomplete_renewals'
                'membership_graceperiod_regular'
                'membership_graceperiod_without_renewals'
                'membership_graceperiod_without_invoice'

            Case #1: Membresías activas, a ser cambiadas a periodo de gracia vencer hoy
                'membership_active_expire_today_without_invoice'
                'membership_active_expire_today'
        """
        self.factory = RequestFactory()
        create_contacts(1)
        add_organization()
        self.user = user = User.objects.create(username='myadmin',email='test@admin.com',password='123456',first_name='Administrator',last_name='GM',is_superuser=True)
        self.memberships = generate_memberships_graceperiod_to_inactive_and_active_to_graceperiod()
    def test_membership_graceperiod_deactivate(self):
        """
                'membership_graceperiod_expired'
                'membership_graceperiod_expire_today'
                'membership_graceperiod_incomplete_renewals'
        :return:
        """

        membership_deactivating(self.now)

        check_memb = Membership.objects.filter(state='inactive').count()
        result = LogEntry.objects.filter(object_repr='Membresia inactiva por falta de pago').count()
        expected = 2
        self.assertEqual(result, expected)
        self.assertEqual(check_memb, expected)

        memb1 = self.memberships['membership_graceperiod_expired']['membership']
        memb2 = self.memberships['membership_graceperiod_expire_today']['membership']
        memb3 = self.memberships['membership_graceperiod_incomplete_renewals']['membership']
        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()

        self.assertEqual(memb1.state, 'inactive')
        self.assertEqual(memb2.state, 'inactive')
        self.assertEqual(memb3.state, 'graceperiod')

    def test_membership_graceperiod_renew_graceperiod(self):
        """ PREGUNTAR SOBRE ESCENARIO
                       'membership_active_expire_today'
                       'membership_active_expire_today_without_invoice'
                       'membership_active_expire_yesterday_without_invoice'
               :return:
               """
        renew_graceperiod(self.now)
        check_memb = Membership.objects.filter(state='graceperiod').count() #already got 6, now we expect tree more
        memb_expected = 9
        self.assertEqual(check_memb, memb_expected)
        result = LogEntry.objects.filter(object_repr='Membresia ha cambiado a periodo de prueba').count()
        logs_expected = 3
        self.assertEqual(result, logs_expected)

        memb1 = self.memberships['membership_active_expire_today']['membership']
        memb2 = self.memberships['membership_active_expire_today_without_invoice']['membership']
        memb3 = self.memberships['membership_active_expire_yesterday_without_invoice']['membership']
        memb1.refresh_from_db()
        memb2.refresh_from_db()
        memb3.refresh_from_db()

        self.assertEqual(memb1.state, 'graceperiod')
        self.assertEqual(memb2.state, 'graceperiod')
        self.assertEqual(memb3.state, 'graceperiod')

