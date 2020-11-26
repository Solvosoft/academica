from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied

def user_group_perms(perm, login_url=None, raise_exception=False):

    def groups_has_perm(user):

        if user.is_superuser:
            return True

        app_label, codename = (perm.split("."))
        permission = Permission.objects.filter(codename=codename, content_type__app_label=app_label).first()

        if permission:
            for group in user.groups.all():
                if permission in group.permissions.all():
                    return True

        if raise_exception:
            raise PermissionDenied

        return False
    return user_passes_test(groups_has_perm, login_url=login_url)