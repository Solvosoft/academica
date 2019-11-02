from async_notifications.register import update_template_context
from django.core.management import BaseCommand

from membership_manager.utils import loademailtemplates


class Command(BaseCommand):
    help = "Load templates command"

    def handle(self, *args, **options):
        loademailtemplates()
