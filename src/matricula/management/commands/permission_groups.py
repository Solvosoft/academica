from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):

        change_profile = Permission.objects.filter(codename="change_profile", content_type__app_label="matricula").first()
        view_group = Permission.objects.filter(codename="view_group", content_type__app_label="matricula").first()
        view_qualifications = Permission.objects.filter(codename="can_view_qualifications", content_type__app_label="matricula").first()
        qualify_students = Permission.objects.filter(codename="can_qualify_students", content_type__app_label="matricula").first()

        permissions_professor = [change_profile, view_group, view_qualifications, qualify_students]
        professor_group = Group(
            name="Profesores"
        )
        professor_group.save()
        professor_group.permissions.add(*permissions_professor)