import calendar
import datetime

from dateutil.relativedelta import relativedelta
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.timezone import now as timezonenow

from membership_manager.models import Membership, MembershipRenew
from membership_manager.renew_utils import get_renew_without_inovice, get_comming_expired_renew
from membership_manager.utils import invoice_expiration_filter_queryset


class ManejadorNotificaciones:
    def get_day_month(self, now=None, today=True):
        if now is None:
            now = timezonenow()

        if today:
            return [now]
        num_days = calendar.monthrange(now.year, now.month)[1]
        return [datetime.datetime(now.year, now.month, day) for day in range(1, num_days + 1)]

    def get_expirations(self):
        days = self.get_day_month(today=False)
        list_invoice = []
        for day in days:
            queryset = invoice_expiration_filter_queryset(now=day)
            for invoice in queryset:
                list_invoice.append(
                    (day, invoice.membership.name,
                     reverse_lazy('admin:membership_manager_membership_change',
                        args=(invoice.membership.id,)),
                     invoice.expiration_date,
                     reverse_lazy('admin:membership_manager_invoice_change',
                                  args=(invoice.id,)),

                     'notification_mail',
                     'pending', 'Invoice')
                )
        return list_invoice

    def simule_renew(self, now, renew):
        newrenew = MembershipRenew(
            membership=renew.membership,
            creation_date=now,
            start_date=now,
            encobro=True,
            end_date=now + relativedelta(
            months=+renew.membership.renewal_period.months)
            )

        return newrenew

    def get_invoice_creation(self):
        days = self.get_day_month(today=False)
        list_invoice = []
        for day in days:
            queryset = get_renew_without_inovice(day)
            for membershiprenew in queryset:
                list_invoice.append(
                        (day, membershiprenew.membership.name,
                         reverse_lazy('admin:membership_manager_membership_change',
                            args=(membershiprenew.membership.id,)),
                         membershiprenew.end_date,
                         str(membershiprenew),
                         'notification_mail',
                         'active', 'MembershipRenew')
                )
            queryset = get_comming_expired_renew(day)
            for memrenew in queryset:
                membershiprenew = self.simule_renew(day, memrenew)
                list_invoice.append(
                        (day, membershiprenew.membership.name,
                         reverse_lazy('admin:membership_manager_membership_change',
                            args=(membershiprenew.membership.id,)),
                         membershiprenew.end_date,
                         str(membershiprenew),
                         'Creación del renew sin correo',
                         'active', 'MembershipRenew')
                )

        return list_invoice

    def dos_periodos_activos(self):
        list_invoice = []

        queryset = Membership.objects.filter(
            Q(state="active") | Q(state='graceperiod'),
        ).annotate(totalmemb=Count('renews', filter=Q(renews__encobro=True, renews__active=True))).filter(
            totalmemb__gte=2
        )

        for membresia in queryset:
            list_invoice.append(
                (membresia.name,
                 reverse_lazy('admin:membership_manager_membership_change',
                              args=(membresia.id,)),
                 "\n || ".join(list(map(lambda x: str(x), membresia.renews.filter(active=True)))),
                 "act: %d encobro: %d " % (membresia.renews.filter(active=True).count(),
                                         membresia.renews.filter(active=True, encobro=True).count()
                                         ),
                 'Sin notificacion',
                 "#",
                 'No hay reparación automática', "")
            )
        return list_invoice

    def activo_sin_encobro(self):
        list_invoice = []
        queryset = MembershipRenew.objects.filter(membership__state="active",
                                       encobro=False,
                                       active=True)

        if queryset.exists():
            list_invoice.append(
                ("Reparar todas las membresías que no tengan cobro",
                 "#",
                 "Todas las membresías con periodo de gracia debería no estar activas",
                 "Repara %d en total"%(queryset.count()),
                 'notification_mail',
                 reverse_lazy('reparar',
                              args=(0, 'encobro')),
                 'Convierte el periodo en periodo de cobro',
                 "ui-widget-header ui-corner-all")
            )
        for membershiprenew in queryset:
            list_invoice.append(
                (membershiprenew.membership.name,
                 reverse_lazy('admin:membership_manager_membership_change',
                              args=(membershiprenew.membership.id,)),
                 membershiprenew.end_date,
                 str(membershiprenew),
                 'notification_mail',
                 reverse_lazy('reparar',
                              args=(membershiprenew.pk, 'encobro')),
                 'Convierte el periodo en periodo de cobro', "")
            )

        return list_invoice

    def sin_factura(self):
        list_invoice = []

        queryset = MembershipRenew.objects.filter(
            Q(membership__state="active")|Q(membership__state='graceperiod'),
                                       encobro=True, active=True, inv_m_renews=None)

        if queryset.exists():

            list_invoice.append(
                ("Reparar todas las membresías generando factura",
                 "#",
                 "Estas membresías no tienen facturas ",
                 "Repara %d en total"%(queryset.count()),
                 'notification_mail',
                 reverse_lazy('reparar',
                              args=(0, 'invoice')),
                 'Crea una factura para el periodo',
                 "ui-widget-header ui-corner-all")
            )
        for membershiprenew in queryset:
            list_invoice.append(
                (membershiprenew.membership.name,
                 reverse_lazy('admin:membership_manager_membership_change',
                              args=(membershiprenew.membership.id,)),
                 membershiprenew.end_date,
                 str(membershiprenew),
                 'notification_mail',
                 reverse_lazy('reparar',
                              args=(membershiprenew.pk, 'invoice')),
                 'Crea una factura para la membresía dada', "")
            )

        return list_invoice

    def experiodo_de_gracia(self):
        list_invoice = []

        queryset = MembershipRenew.objects.filter(
                Q(start_date__date=datetime.datetime(year=2020, month=1, day=1).date(),
                end_date__date=datetime.datetime(year=2020, month=2, day=1).date())|Q(
                    start_date__date=datetime.datetime(year=2020, month=2, day=1).date(),
                end_date__date=datetime.datetime(year=2020, month=2, day=2).date())
        )

        if queryset.exists():
            list_invoice.append(
                ("Eliminar periodos creados automáticamente",
                 "#",
                 "Estos periodos fueron creados para mantener activa las membresías",
                 "Repara %d en total" % (queryset.count()),
                 'notification_mail',
                 reverse_lazy('reparar',
                              args=(0, 'graceperiod')),
                 'Elimina el periodo',
                 "ui-widget-header ui-corner-all")
            )
        for membershiprenew in queryset:
            list_invoice.append(
                (membershiprenew.membership.name,
                 reverse_lazy('admin:membership_manager_membership_change',
                              args=(membershiprenew.membership.id,)),
                 membershiprenew.end_date,
                 str(membershiprenew),
                 'notification_mail',
                 reverse_lazy('reparar',
                              args=(membershiprenew.pk, 'graceperiod')),
                 'Elimina el periodo', "")
            )

        return list_invoice

    def membresias_inactive_renovacion(self):
        list_invoice = []
        queryset = Membership.objects.filter(
            state="inactive",
            renews__active=True
        )
        if queryset.exists():
            list_invoice.append(
                ("La membresía está inactiva pero tiene renovaciones activas",
                 "#",
                 mark_safe('<a href="%s" target="_blank">Poner membresia activa </a>' % (
                     reverse_lazy('reparar', args=(   0, 'poneactiva'))),),
                 "Repara %d en total" % (queryset.count()),
                 'notification_mail',
                 reverse_lazy('reparar',
                              args=(0, 'setinactiverenew')),
                 'Pone periodo inactivo',
                 "ui-widget-header ui-corner-all")
            )
        for membership in queryset:
            list_invoice.append(
                (membership.name,
                 reverse_lazy('admin:membership_manager_membership_change',
                              args=(membership.id,)),
                 mark_safe('<a href="%s" target="_blank">Poner membresia activa </a>'%reverse_lazy('reparar',
                              args=(membership.pk, 'poneactiva'))),
                 str(membership),
                 'notification_mail',
                 reverse_lazy('reparar',
                              args=(membership.pk, 'setinactiverenew')),
                 'Desactivar periodo', "")
            )
        return list_invoice

    def get_inconsistencias(self):
        days = self.get_day_month()
        list_invoice = []
        list_invoice += self.membresias_inactive_renovacion()
        list_invoice += self.experiodo_de_gracia()
        list_invoice += self.activo_sin_encobro()
        list_invoice += self.sin_factura()
        list_invoice += self.dos_periodos_activos()

        return list_invoice