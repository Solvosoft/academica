from django.core.management import BaseCommand
from matricula.utils import load_email_temp_academica


class Command(BaseCommand):
    help = "Load templates in académica"

    def handle(self, *args, **options):
        load_email_temp_academica()
