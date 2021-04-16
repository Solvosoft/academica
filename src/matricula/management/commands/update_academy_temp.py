from django.core.management import BaseCommand
from async_notifications.register import update_template_context


class Command(BaseCommand):
    help = "Update email templates in académica"

    def handle(self, *args, **options):
        update_template_context(
        'email_enroll_removed', 'Lo sentimos, Tu MATRÍCULA ha sido eliminada por no realizarse el pago',
        [('group'),("domain"),("hours_to_pay")], 'email_enroll_removed.html', as_template=True)

