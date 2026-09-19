from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = ("Instalación/actualización idempotente: migraciones, tabla de caché, "
            "grupos de permisos y plantillas de correo. Se ejecuta en cada despliegue.")

    def handle(self, *args, **options):
        call_command('migrate', interactive=False)
        call_command('createcachetable')
        call_command('permission_groups')
        call_command('load_email_templates')
