from django.core.management.base import BaseCommand, CommandError

from matricula.contrib.bills.webcheckout import WebCheckoutError, sync_course_product
from matricula.models import Course


class Command(BaseCommand):
    help = "Crea o actualiza en el servicio de pagos con tarjeta el producto de cada curso."

    def add_arguments(self, parser):
        parser.add_argument('--course', type=int, help="Sincroniza solo este curso (id)")

    def handle(self, *args, **options):
        courses = Course.objects.all()
        if options['course']:
            courses = courses.filter(pk=options['course'])
        errors = 0
        for course in courses:
            try:
                product_id = sync_course_product(course)
                self.stdout.write("%s -> %s" % (course, product_id))
            except WebCheckoutError as exc:
                errors += 1
                self.stderr.write("%s: %s" % (course, exc))
        if errors:
            raise CommandError("%d cursos no se pudieron sincronizar" % errors)
