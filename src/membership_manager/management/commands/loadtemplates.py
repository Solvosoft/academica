from async_notifications.register import update_template_context
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Load templates command"

    def handle(self, *args, **options):
        update_template_context('pay_mail',
                                'Pago de membresía - Código Sur',
                                [('desc', 'Correo automático para el pago de membresias'), ],
                                'pay_email.html',
                                as_template=True)

        update_template_context('welcome_mail',
                                'Bienvenido(a) - Código Sur',
                                [('desc', 'Correo automatico de bienvenida a Código Sur'), ],
                                'subscribe_email.html',
                                as_template=True)

        update_template_context("notification_mail",
                                'Nuevo Aviso - Código Sur',
                                [('desc', 'Recordatorios automaticos de los pagos pendientes'), ],
                                'pay_email.html',
                                as_template=True)
