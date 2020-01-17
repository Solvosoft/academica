from datetime import datetime

from django.core.management import BaseCommand
import csv

from django.utils.timezone import now

from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import Organization, Membership, MembershipRenew


class Command(BaseCommand):
    help = "Load templates command"

    def handle(self, *args, **options):
         sin_orga =[]
         membresias_noactivas = []
         moneda = {'USD':  SystemCurrency.objects.get(pk=4), 'ARS': SystemCurrency.objects.get(pk=5)}
         period = RenewalPeriod.objects.get(pk=5)
         with open('/home/luisza/Desktop/faltentes.csv', newline='') as csvfile:
            lector = csv.reader(csvfile, delimiter=';', quotechar='"')
            for linea in lector:
                org = Organization.objects.filter(name=linea[3]).first()
                if org is None:
                    sin_orga.append(linea)
                    continue

                d = [x.pk for x in org.membership_set.all()]
                if len(d) != 0:
                    membresias_noactivas.append(
                        (org.pk, d)
                    )
                    continue
                #print(linea)
                mem = Membership.objects.create(
                    membership_type = "Organizacional",
                    contact = None,
                    organization = org,
                    name =linea[3],
                    annual_cost = float(linea[4]),
                    currency = moneda[linea[5]],
                    description = linea[3].strip(" www"),
                    renewal_period =period,
                    state = 'active'
                )

                MembershipRenew.objects.create(
                    creation_date=now(),
                    membership = mem,
                    start_date =datetime(2019, 1, 1),
                    end_date =datetime(2020, 1, 1),
                    graceperiod = False,
                    active = True
                )

                MembershipRenew.objects.create(
                    creation_date=now(),
                    membership=mem,
                    start_date=datetime(2020, 1, 1),
                    end_date=datetime(2020, 2, 1),
                    graceperiod=True,
                    active=True
                )


            print("#######SIN ORGA ############")
            print(sin_orga)
            print("########### CON NO ACTIVAS #########")
            print(membresias_noactivas)
                #print(linea)