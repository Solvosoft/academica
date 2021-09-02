from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand
from djgentelella.models import MenuItem
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class Command(BaseCommand):

    def handle(self, *args, **options):

        change_profile = Permission.objects.filter(codename="change_profile", content_type__app_label="matricula").first()
        view_group = Permission.objects.filter(codename="view_group", content_type__app_label="matricula").first()
        view_qualifications = Permission.objects.filter(codename="can_view_qualifications", content_type__app_label="matricula").first()
        qualify_students = Permission.objects.filter(codename="can_qualify_students", content_type__app_label="matricula").first()
        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()

        permissions_professor = [change_profile, view_group, view_qualifications, qualify_students, view_reports]
        professor_group = Group.objects.filter(name=settings.PROFESSOR_GROUP_NAME).first()
        if not professor_group:
            professor_group = Group(name=settings.PROFESSOR_GROUP_NAME)
            professor_group.save()
        professor_group.permissions.add(*permissions_professor)

        ct = ContentType.objects.get_for_model(MenuItem)
        # admin group to académica.
        enroll_perms = Permission.objects.filter(
            content_type__app_label="matricula").all()
        djgentelella_perms = Permission.objects.filter(
            content_type__app_label="djgentelella", content_type=ct).all()
        bill_perms = Permission.objects.filter(
            content_type__app_label="bills").all()
        change_systemcurrency = Permission.objects.filter(codename="change_systemcurrency", content_type__app_label="membership_core").first()
        view_systemcurrency = Permission.objects.filter(codename="view_systemcurrency", content_type__app_label="membership_core").first()
        add_systemcurrency = Permission.objects.filter(codename="add_systemcurrency", content_type__app_label="membership_core").first()
        delete_systemcurrency = Permission.objects.filter(codename="delete_systemcurrency", content_type__app_label="membership_core").first()
        dashboard_systemcurrency = Permission.objects.filter(codename="can_show_dashboard", content_type__app_label="membership_core").first()
        add_user = Permission.objects.filter(codename="add_user", content_type__app_label="auth").first()
        permissions_systemcurrency = [dashboard_systemcurrency, change_systemcurrency, view_systemcurrency, add_systemcurrency, delete_systemcurrency, add_user]
        enroll_group = Group.objects.filter(name=settings.ADMIN_GROUP_NAME).first()
        if not enroll_group:
            enroll_group = Group(name=settings.ADMIN_GROUP_NAME)
            enroll_group.save()
        enroll_group.permissions.add(*enroll_perms)
        enroll_group.permissions.add(*bill_perms)
        enroll_group.permissions.add(*djgentelella_perms)
        enroll_group.permissions.add(*permissions_systemcurrency)
