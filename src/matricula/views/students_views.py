import json

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django_ajax.decorators import ajax

from matricula.decorators import user_group_perms
from matricula.forms import QualifyStudentForm
from matricula.models import Enroll, Group, Professor
from matricula.views.utils import checking_professor


@user_group_perms(perm='matricula.can_view_qualifications')
def qualify_students(request, pk):
    if not checking_professor(request):
        return redirect(reverse('courses'))
    group = get_object_or_404(Group, pk=pk)
    enroll_list = Enroll.objects.filter(group=group)
    if group.is_paid:
        enroll_list = enroll_list.filter(bill__is_paid=True)
    context = {'group': group,
               'form': QualifyStudentForm(),
               'enroll_list': enroll_list}

    return render(request, "students/qualify_students.html", context=context)


@ajax
def update_enroll(request):
    if not checking_professor(request):
        return redirect(reverse('courses'))
    if request.is_ajax():
       enroll_list = json.loads(request.body)

       for enroll in enroll_list:
           Enroll.objects.filter(pk=int(enroll['pk'])).update(course_score=float(enroll['Nota']), course_status=enroll['Estado'])


@ajax
def update_enroll_status(request, pk, status):
    if not checking_professor(request):
        return redirect(reverse('courses'))
    if request.is_ajax():
       enroll_list = json.loads(request.body)

       for enroll in enroll_list:
           Enroll.objects.filter(pk=int(enroll['pk']), group__pk=pk).update(course_status=status)