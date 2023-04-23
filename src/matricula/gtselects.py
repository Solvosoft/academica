from django.contrib.auth.models import Permission, User

from djgentelella.groute import register_lookups
from djgentelella.views.select2autocomplete import BaseSelect2View

from matricula.models import Period
from matricula.views.utils import get_active_period
from matricula.models import Category, FakeGroup, Student
from django.db.models import Value, F
from django.db.models.functions import Concat


@register_lookups(prefix="category", basename="categorybasename")
class CategoryGModelLookup(BaseSelect2View):
    model = Category
    fields = ['name']


@register_lookups(prefix="student", basename="student")
class StudentGModelLookup(BaseSelect2View):
    model = Student
    fields = ['organization']

    def get_queryset(self):
        queryset = Student.objects.order_by('organization').distinct()
        q = self.request.GET.get('q', None)
        if q is not None:
            queryset = queryset.filter(organization__unaccent__icontains=q).order_by('organization').distinct('organization')
        return queryset


@register_lookups(prefix="permission", basename="permission")
class PermissionGModelLookup(BaseSelect2View):
    model = Permission
    fields = ['name']


@register_lookups(prefix="period", basename="periodbasename")
class PeriodGModelLookup(BaseSelect2View):
    model = Period

    def get_queryset(self):
        return get_active_period()


@register_lookups(prefix="user", basename="user")
class UserProfessorGModelLookup(BaseSelect2View):
    model = User
    fields = ['full_name', 'email']

    def get_queryset(self):
        queryset=super().get_queryset().annotate(
            full_name=Concat('first_name', Value(' '), 'last_name'),
        )

        return queryset


@register_lookups(prefix="studentuser", basename="studentuser")
class UserProfessorGModelLookup(BaseSelect2View):
    model = User
    fields = ['username']

    def get_queryset(self):
        queryset = User.objects.filter(professor__isnull=True, is_active=True)
        return queryset


@register_lookups(prefix="studentuserbase", basename="studentuserbase")
class UserStudentGModelLookup(BaseSelect2View):
    model = User
    fields = ['username']

    def get_queryset(self):
        q = self.request.GET.get('q', None)
        queryset = User.objects.filter(student__isnull=True, is_active=True)
        if q is not None:
            queryset = queryset.filter(username__icontains=q)
        return queryset


@register_lookups(prefix="groups", basename="fakegroupsbase")
class GroupGModelLookup(BaseSelect2View):
    model = FakeGroup
    fields = ['name']


@register_lookups(prefix="studentenroll", basename="studentenroll")
class StudentGModelLookup(BaseSelect2View):
    model = Student
    fields = ['full_name']

    def get_queryset(self):
        queryset = Student.objects.filter(user__is_active=True).annotate(
            full_name=Concat('user__first_name', Value(' '), 'user__last_name'), 
        )
        return queryset


@register_lookups(prefix="studentsearch", basename="studentsearch")
class UserStudentGModelLookup(BaseSelect2View):
    model = Student
    fields = ['full_name', 'email']

    def get_queryset(self):
        queryset = Student.objects.all().annotate(
            full_name=Concat('user__first_name', Value(' '), 'user__last_name'),
            email=F('user__email')
        )
        return queryset