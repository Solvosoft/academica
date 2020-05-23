from dateutil.relativedelta import relativedelta
from django.test import TestCase

# last_renew_start_date
from django.utils.timezone import now

from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import MembershipRenew, Membership


class RenewStartDateTestCase(TestCase):
    """
    Escenario:
    El sistema actualiza la fecha de inicio del últumo periodo activo.

    Posibles casos de falla:
        - Existen 2 MembershipRenew de una misma membresia activos, el primero es más antiguo que el
        segundo.  El sistema debería seleccionar el segundo ya que corresponde al último periodo en cobro de la membresia

        Comportamiento esperado:  El sistema debe siempre seleccionar el MembershipRenew en cobro y activo más nuevo.

        - Existen 2 MembershipRenew encobro=False pero con una activa.
                El sistema debe retornar el end_date del renew activo.

    """
    fixtures = ['async_notifications_email_template.json', 'async_notifications_template_context.json', 'membership_core.json']

    def setUp(self):
        self.now = now().date()
        self.membership = Membership.objects.create(
            creation_date=now(),
            membership_type="Personal",
            annual_cost=120,
            currency=SystemCurrency.objects.first(),
            state="active",
            renewal_period=RenewalPeriod.objects.first()
        )


    # last_renew_start_date
    def test_lrsd_base(self):
        """
        Caso base, debe seleccionarse la segunda por estar posterior en el tiempo
        """
        ok_date = self.now+relativedelta(months=+1)
        MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = self.now+relativedelta(months=-1),
            end_date = self.now+relativedelta(months=+1),
            encobro = True,
            active = True,
        )
        MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = ok_date,
            end_date = self.now+relativedelta(months=+2),
            encobro = True,
            active = True,
        )
        self.assertEqual(ok_date, self.membership.last_renew)
    def test_lrsd_inactive(self):
        """
        La segunda renew no puede seleccionarse porque está inactiva

        """
        ok_date = self.now+relativedelta(months=-1)
        MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = ok_date,
            end_date = self.now+relativedelta(months=+1),
            encobro = True,
            active = True,
        )
        MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = self.now+relativedelta(months=+1),
            end_date = self.now+relativedelta(months=+2),
            encobro = True,
            active = False,
        )
        self.assertEqual(ok_date, self.membership.last_renew)
    def test_lrsd_encobro_false(self):
        """ La segunda renew no puede seleccionarse xq no está en cobro"""
        ok_date = self.now+relativedelta(months=-1)
        MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = ok_date,
            end_date = self.now+relativedelta(months=+1),
            encobro = True,
            active = True,
        )
        MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = self.now+relativedelta(months=+1),
            end_date = self.now+relativedelta(months=+2),
            encobro = False,
            active = True,
        )
        self.assertEqual(ok_date, self.membership.last_renew)
    def test_lrsd_2renew_vigentes_fechasfin_iguales(self):
        """
        Dos renew con la misma fecha de finalizado vigentes
        debería seleccionarse siempre el segundo renew ya que se toma
        como criterio de segundo ordenamiento el pk
        """
        ok_date = self.now+relativedelta(months=+1)
        MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = self.now+relativedelta(months=-1),
            end_date = self.now+relativedelta(months=+2),
            encobro = True,
            active = True,
        )
        MembershipRenew.objects.create(
            creation_date=now(),
            membership = self.membership,
            start_date = ok_date,
            end_date = self.now+relativedelta(months=+2),
            encobro = True,
            active = True,
        )
        self.assertEqual(ok_date, self.membership.last_renew)
    def test_lrsd_sin_ninguna_retorna_none(self):
        """
        Si ninguna cumple criterios retorna None
        se escogió la configuración encobro=False en las 2 porque es un escenario bastante probable
        """
        ok_date = self.now + relativedelta(months=-1)
        MembershipRenew.objects.create(
            creation_date=now(),
            membership=self.membership,
            start_date=ok_date,
            end_date=self.now + relativedelta(months=+1),
            encobro=False,
            active=True,
        )
        MembershipRenew.objects.create(
            creation_date=now(),
            membership=self.membership,
            start_date=self.now + relativedelta(months=+1),
            end_date=self.now + relativedelta(months=+2),
            encobro=False,
            active=True,
        )
        self.assertEqual(None, self.membership.last_renew)