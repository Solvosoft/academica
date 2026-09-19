import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.db.models.expressions import Q
from django.views.generic import ListView

from matricula.ajax import ajax

from matricula.forms import QualifyStudentForm
from matricula.models import Enroll, Group


VALID_STATUSES = {'approved', 'reproved', 'uncompleted', 'never_attend', None}


def can_grade(user, group):
    """Califica el superusuario, administración académica o un profesor activo del grupo."""
    if not user.is_authenticated:
        return False
    if user.is_superuser or user.groups.filter(name=settings.ADMIN_GROUP_NAME).exists():
        return True
    professor = getattr(user, 'professor', None)
    return bool(professor and professor.active and group.professors.filter(pk=professor.pk).exists())


@login_required
def qualify_students(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if not can_grade(request.user, group):
        messages.error(request, _("The professor associated with this user is not active"))
        return redirect(reverse('groups_enroll'))
    enroll_list = Enroll.objects.filter(group=group, enroll_finished=True).order_by('student__user__first_name')
    if group.is_paid:
        enroll_list = enroll_list.filter(Q(bill__is_paid=True) | Q(paid_excluded=True))
    context = {'group': group,
               'form': QualifyStudentForm(),
               'enroll_list': enroll_list}
    return render(request, "students/qualify_students.html", context=context)


@ajax
@login_required
def update_enroll(request):
    """Guarda el estado de cada matrícula; solo en grupos que el usuario puede calificar."""
    allowed_groups = {}
    for enroll in json.loads(request.body or b'[]'):
        if not enroll.get('pk') or enroll.get('Estado') not in VALID_STATUSES:
            continue
        item = Enroll.objects.filter(pk=int(enroll['pk'])).select_related('group').first()
        if item is None:
            continue
        if item.group_id not in allowed_groups:
            allowed_groups[item.group_id] = can_grade(request.user, item.group)
        if not allowed_groups[item.group_id]:
            return HttpResponseForbidden()
        updatedata = {'course_status': enroll['Estado'],
                      'go_to_one_class': enroll['Estado'] != 'never_attend'}
        if enroll['Estado'] == "reproved":
            updatedata['pdf_certificate'] = None
        Enroll.objects.filter(pk=item.pk).update(**updatedata)


@ajax
@login_required
def update_enroll_status(request, pk, status):
    group = get_object_or_404(Group, pk=pk)
    if not can_grade(request.user, group) or status not in VALID_STATUSES:
        return HttpResponseForbidden()
    pks = [int(enroll['pk']) for enroll in json.loads(request.body or b'[]') if enroll and enroll.get('pk')]
    items = Enroll.objects.filter(pk__in=pks, group=group)
    if status in ["reproved", 'uncompleted', 'never_attend']:
        items.update(pdf_certificate=None)
    items.update(course_status=status)


@method_decorator(login_required, name='dispatch')
class GradeList(ListView):
    template_name = "students/grates_history.html"
    model = Enroll
    paginate_by = 300

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'student'):
            queryset = queryset.filter(student=self.request.user.student, enroll_finished=True)
        else:
            queryset = queryset.none()
        return queryset
