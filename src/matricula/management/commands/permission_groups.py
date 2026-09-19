from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand
from django.db.models import Q

from matricula.models import FakeGroup

PROFESSOR_PERMISSIONS = [
    'matricula.change_profile',
    'matricula.view_group',
    'matricula.can_view_qualifications',
    'matricula.can_qualify_students',
    'matricula.view_reports',
]

ADMIN_EXTRA_PERMISSIONS = [
    'membership_core.can_show_dashboard',
    'membership_core.view_systemcurrency',
    'membership_core.add_systemcurrency',
    'membership_core.change_systemcurrency',
    'membership_core.delete_systemcurrency',
    'membership_core.view_country',
    'membership_core.add_country',
    'membership_core.change_country',
    'membership_core.delete_country',
    'auth.add_user',
]


def get_permissions(names):
    query = Q(pk__in=[])
    for name in names:
        app_label, codename = name.split('.')
        query |= Q(content_type__app_label=app_label, codename=codename)
    return Permission.objects.filter(query)


class Command(BaseCommand):
    help = "Crea (o actualiza) los grupos de Profesores y Administradores con sus permisos."

    def handle(self, *args, **options):
        professor_group, _ = Group.objects.get_or_create(name=settings.PROFESSOR_GROUP_NAME)
        professor_group.permissions.add(*get_permissions(PROFESSOR_PERMISSIONS))

        admin_group, _ = Group.objects.get_or_create(name=settings.ADMIN_GROUP_NAME)
        admin_group.permissions.add(*Permission.objects.filter(
            Q(content_type__app_label__in=['matricula', 'bills']) |
            Q(content_type__app_label='djgentelella', content_type__model='menuitem')))
        admin_group.permissions.add(*get_permissions(ADMIN_EXTRA_PERMISSIONS))

        for group in (professor_group, admin_group):
            FakeGroup.objects.get_or_create(group=group, defaults={'name': group.name})

        self.stdout.write(self.style.SUCCESS("Grupos de permisos actualizados"))
