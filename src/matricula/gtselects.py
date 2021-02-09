from djgentelella.groute import register_lookups
from djgentelella.views.select2autocomplete import BaseSelect2View
from .models import Category, Student
from matricula.models import Period
from django.contrib.auth.models import Permission
from datetime import datetime
from matricula.views.utils import get_active_period


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
            queryset = queryset.filter(organization__icontains=q).order_by('organization').distinct('organization')
        return queryset


@register_lookups(prefix="permission", basename="permission")
class PermissionGModelLookup(BaseSelect2View):
    model = Permission
    fields = ['name']


@register_lookups(prefix="period", basename="periodbasename")
class PeriodGModelLookup(BaseSelect2View):
    model = Period
    fields = ['name']

    def get_queryset(self):
        return get_active_period()
