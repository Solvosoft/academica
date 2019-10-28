from async_notifications.register import update_template_context
from django.core.management import BaseCommand
from django.utils import timezone
from faker import Faker
from membership_manager.task_utils import *

from membership_core.models import SystemCurrency, Service, RenewalPeriod
from membership_manager.models import Contact, Organization, Membership, MembershipRenew
from membership_manager.tests_utils import add_organization, create_contacts, generate_memberships_to_notify_graceperiod


class Command(BaseCommand):
    help = "Load templates command"
    fake = Faker()
    contacts_num = 10
    memb_num = 2
    fails = 2
    contacts_ids = []
    contact_qset = None
    services_list = [service
                     for service in Service.objects.all()]
    renewal_period_list = [renewal
                     for renewal in RenewalPeriod.objects.all()]
    now = timezone.now()



    def handle(self, *args, **options):
        create_contacts(3)
        add_organization()
        generate_memberships_to_notify_graceperiod()
        # self.check_with_tasks()
