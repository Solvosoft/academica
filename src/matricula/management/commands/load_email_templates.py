from django.core.management.base import BaseCommand

from matricula.utils import load_email_templates


class Command(BaseCommand):
    help = "Crea las plantillas de correo que falten (--overwrite las reemplaza todas)."

    def add_arguments(self, parser):
        parser.add_argument('--overwrite', action='store_true',
                            help="Reemplaza asunto y mensaje con los de los archivos .html")

    def handle(self, *args, **options):
        created = load_email_templates(overwrite=options['overwrite'])
        self.stdout.write(self.style.SUCCESS(
            "Plantillas actualizadas: %s" % (", ".join(created) or "ninguna")))
