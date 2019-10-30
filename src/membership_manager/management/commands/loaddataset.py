from django.core.management import BaseCommand

from membership_manager.tests.tests_utils import generate_memberships_to_notify_graceperiod


class Command(BaseCommand):
    help = "Load templates command"

    def handle(self, *args, **options):
        generate_memberships_to_notify_graceperiod()
        # self.check_with_tasks()
