from django.core.management import BaseCommand
from async_notifications.register import update_template_context
from async_notifications.models import EmailTemplate, TemplateContext


class Command(BaseCommand):
    help = "Update email templates in académica"

    def handle(self, *args, **options):
        templates = [
            'set_email_first_academy',
            'email_recovery_academy',
        ]

        EmailTemplate.objects.filter(code__in=templates).delete()
        TemplateContext.objects.filter(code__in=templates).delete()

        update_template_context(
            'set_email_first_academy', 'Sólo un paso más para registrarte - UPo.',
            [('url'), ('student'),("domain")], 'set_email_first.html',
            as_template=True)

        update_template_context(
        'email_recovery_academy', 'Correo de recuperación de contraseña',
        [('user'), ('student'), ('url'), ("domain")], 'email_recovery.html',
        as_template=True)
