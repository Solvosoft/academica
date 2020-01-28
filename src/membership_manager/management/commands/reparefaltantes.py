from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand
import csv

from django.utils.timezone import now

from membership_core.models import SystemCurrency, RenewalPeriod
from membership_manager.models import Organization, Membership, MembershipRenew


class Command(BaseCommand):
    help = "Load templates command"

    def handle(self, *args, **options):

         with open('~/tblorders.csv', newline='') as csvfile:
            lector = csv.reader(csvfile, delimiter=',', quotechar='"')
            for linea in lector:
                mem = Membership.objects.filter(organization__name=linea[0]).first()
                datestart = datetime_object = datetime.strptime(linea[1], '%Y-%m-%d %H:%M:%S')
                mem.renews.all().delete()
                nowdate = now()
                dateini = datestart

                while dateini.year != nowdate.year:
                    enddate = dateini + relativedelta(months=+12)
                    encobro = False
                    active = False
                    print(dateini, enddate)
                    if enddate.year == nowdate.year:
                        encobro = True
                        active = True
                    MembershipRenew.objects.create(
                        creation_date=nowdate,
                        membership = mem,
                        start_date = dateini,
                        end_date = enddate,
                        encobro = encobro,
                        active = active
                    )
                    dateini = enddate