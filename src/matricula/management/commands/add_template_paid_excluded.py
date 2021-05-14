from django.core.management import BaseCommand
from async_notifications.register import update_template_context


class Command(BaseCommand):
    help = "Update email templates in académica"

    def handle(self, *args, **options):

        update_template_context(
            'enroll_paid_excluded', 'Correo de beca completa asignada - UPo',
            [('user'), ('url'),("domain"),('group')],
            'enroll_paid_excluded.html', as_template=True)
