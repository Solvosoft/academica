import json

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.decorators import method_decorator
from django.db.models.expressions import Q
from django.views.generic import ListView

from django_ajax.decorators import ajax

from matricula.decorators import user_group_perms
from matricula.forms import QualifyStudentForm
from matricula.models import Enroll, Group


@user_group_perms(perm='matricula.can_view_qualifications')
def qualify_students(request, pk):
    if hasattr(request.user, 'professor') and request.user.professor.active:
        group = get_object_or_404(Group, pk=pk)
        enroll_list = Enroll.objects.filter(group=group, enroll_finished=True).order_by('student__user__first_name')
        if group.is_paid:
            enroll_list = enroll_list.filter(Q(bill__is_paid=True) | Q(paid_excluded=True))
        context = {'group': group,
                'form': QualifyStudentForm(),
                'enroll_list': enroll_list}
    else:
        messages.error(request, _("The professor associated with this user is not active"))
        return redirect(reverse('groups_enroll'))

    return render(request, "students/qualify_students.html", context=context)


@ajax
def update_enroll(request):
    if request.is_ajax():
        enroll_list = json.loads(request.body)

        for enroll in enroll_list:
            item = Enroll.objects.filter(pk=int(enroll['pk']))
            updatedata={'course_status': enroll['Estado']}
            if enroll['Estado'] == "reproved":
                updatedata['pdf_certificate']=None
            if enroll['Estado'] == 'never_attend':
                updatedata['go_to_one_class']=False
            else:
                updatedata['go_to_one_class']=True
            item.update(**updatedata)


@ajax
def update_enroll_status(request, pk, status):
    if request.is_ajax():
        enroll_list = json.loads(request.body)

        for enroll in enroll_list:
            if not enroll:
                continue
            items = Enroll.objects.filter(pk=int(enroll['pk']), group__pk=pk)
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
