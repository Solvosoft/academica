import calendar
import datetime

from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.utils.timezone import now as timezonenow

from membership_manager.models import Membership, MembershipRenew
from membership_manager.utils import invoice_expiration_filter_queryset, renewal_expiration_filter_manager


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

    def get_invoice_creation(self):
        days = self.get_day_month()
        list_invoice = []
        for day in days:
            queryset = renewal_expiration_filter_manager(day)
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
        return list_invoice

    def dos_periodos_activos(self):
        list_invoice = []

        queryset = Membership.objects.filter(
            Q(state="active") | Q(state='graceperiod'),
        ).annotate(totalmemb=Count('renews', filter=Q(renews__graceperiod=False, renews__active=True))).filter(
            totalmemb__gt=2
        )
        if queryset.exists():
            list_invoice.append(
                ("Poner todas las renovaciones de membresía desactivas excepto la última",
                 "#",
                 "Estas membresías tienen más 2 un periodo activo ",
                 "Repara %d en total" % (queryset.count()),
                 'Sin notificación',
                 reverse_lazy('reparar',
                              args=(0, '2active')),
                 'Desactiva todas las renovaciones excepto la última',
                 "ui-widget-header ui-corner-all")
            )

        for membresia in queryset:
            list_invoice.append(
                (membresia.name,
                 reverse_lazy('admin:membership_manager_membership_change',
                              args=(membresia.id,)),
                 "\n || ".join(list(map(lambda x: str(x), membresia.renews.filter(active=True)))),
                 "act: %d grace: %d " % (membresia.renews.filter(active=True).count(),
                                         membresia.renews.filter(active=True, graceperiod=True).count()
                                         ),
                 'Sin notificacion',
                 reverse_lazy('reparar',
                              args=(membresia.id, '2active')),
                 'Genera un periodo activo para la membresía tomando la fecha de vencimiento mayor', "")
            )
        return list_invoice

    def activo_con_periodo_de_gracia(self):
        list_invoice = []
        queryset = MembershipRenew.objects.filter(membership__state="active",
                                       graceperiod=True,
                                       active=True)

        if queryset.exists():

            list_invoice.append(
                ("Reparar todas las membresías en periodo de gracia",
                 "#",
                 "Todas las membresías con periodo de gracia debería no estar activas",
                 "Repara %d en total"%(queryset.count()),
                 'notification_mail',
                 reverse_lazy('reparar',
                              args=(0, 'graceperiod')),
                 'Convierte la membresías a graceperiod',
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
                              args=(membershiprenew.membership.id, 'graceperiod')),
                 'Convierte la membresías a graceperiod', "")
            )

        return list_invoice

    def dosomasomenos_peridodos_activos(self):
        list_invoice = []
        queryset = Membership.objects.filter(Q(state="active") | Q(state='graceperiod'),
                                             renews__graceperiod=True,
                                             renews__active=True)
        for membresia in queryset:
            if membresia.renews.filter(active=True).count() != 2:
                list_invoice.append(
                    (membresia.name,
                     reverse_lazy('admin:membership_manager_membership_change',
                                  args=(membresia.id,)),
                     "\n || ".join(list(map(lambda x: str(x), membresia.renews.filter(active=True)))),
                     "act: %d grace: %d " % (membresia.renews.filter(active=True).count(),
                                             membresia.renews.filter(active=True, graceperiod=True).count()
                                             ),
                     'Sin notificacion',
                     reverse_lazy('reparar',
                                  args=(membresia.id, '2renews')),
                     'Genera un periodo activo para la membresía tomando la fecha de vencimiento mayor', "")
                )

        if list_invoice:
            list_invoice.insert(0,
                ("Intenta dejar una sola renovación activa",
                 "#",
                 "Varios problemas con las renovaciones",
                 "Repara %d en total"%(len(list_invoice)),
                 'notification_mail',
                  reverse_lazy('reparar',
                              args=(0, '2renews')),
                 'Deshabilita todas las renovaciones y pone la última como activa',
                 "ui-widget-header ui-corner-all")
            )
        return list_invoice

    def sin_factura(self):
        list_invoice = []

        queryset = MembershipRenew.objects.filter(Q(membership__state="active")|Q(membership__state='graceperiod'),
                                       graceperiod=False, active=True, inv_m_renews=None)

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
                              args=(membershiprenew.membership.id, 'invoice')),
                 'Crea una factura para la membresía dada', "")
            )

        return list_invoice
    def get_inconsistencias(self):
        days = self.get_day_month()
        list_invoice = []
        list_invoice += self.dos_periodos_activos()
        list_invoice += self.activo_con_periodo_de_gracia()
        list_invoice += self.dosomasomenos_peridodos_activos()
        list_invoice += self.sin_factura()


        return list_invoice