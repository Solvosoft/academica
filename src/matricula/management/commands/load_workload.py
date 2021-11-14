from django.core.management import BaseCommand
from matricula.models import Course

class Command(BaseCommand):
    help = "Actualiza carga horaria"

    def handle(self, *args, **options):
        ids=[[13, 20],
         [15, 20],
         [21, 20],
         [23, 5],
         [10, 20],
         [8, 5],
         [17, 5],
         [14, 5],
         [19, 5],
         [11, 5],
         [9, 5],
         [12, 20],
         [20, 20],
         [22, 24],
         [16, 20]]
        for c in ids:
            Course.objects.filter(pk=c[0]).update(workload=c[1])