import json
from unicodedata import decimal

from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django_ajax.decorators import ajax

from matricula.forms import QualifyStudentForm
from matricula.models import Enroll, Group


def qualify_students(request, pk):

    group = get_object_or_404(Group, pk=pk)
    enroll_list = Enroll.objects.filter(group=group)

    context = {'group': group,
               'form': QualifyStudentForm(),
               'enroll_list': enroll_list}

    return render(request, "students/qualify_students.html", context=context)


def save_quality_student(request, pk_enroll, pk_group):

    if request.method == "POST":

        form = QualifyStudentForm(request.POST)

        if form.is_valid():

            enroll = Enroll.objects.filter(pk=pk_enroll).first()

            if enroll:
                enroll.course_status = form.cleaned_data['course_status']
                enroll.save()
                messages.success(request, "Datos actualizados exitosamente.")
                return redirect('qualify_students', pk=pk_group)

@ajax
def update_enroll(request):

    if request.is_ajax():
       enroll_list = json.loads(request.body)

       for enroll in enroll_list:
           Enroll.objects.filter(pk=int(enroll['pk'])).update(course_score=float(enroll['Nota']), course_status=enroll['Estado'])


@ajax
def update_enroll_status(request, pk, status):

    if request.is_ajax():
       enroll_list = json.loads(request.body)

       for enroll in enroll_list:
           Enroll.objects.filter(pk=int(enroll['pk']), group__pk=pk).update(course_status=status)