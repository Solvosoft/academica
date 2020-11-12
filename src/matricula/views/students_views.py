from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect

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
                enroll.course_score = form.cleaned_data['course_score']
                enroll.course_status = form.cleaned_data['course_status']
                enroll.save()
                messages.success(request, "Datos actualizados exitosamente.")
                return redirect('qualify_students', pk=pk_group)


def save_quality_students(request, pk_enroll_list, pk_group):

    queryset = Enroll.objects.filter(pk__in=list(pk_enroll_list))

    if request.method == "POST":

        form = QualifyStudentForm(request.POST)

        if form.is_valid():

            if queryset:

                queryset.update(course_score=form.cleaned_data['course_score'], course_status=form.cleaned_data['course_status'])
                messages.success(request, "Datos actualizados exitosamente.")
                return redirect('qualify_students', pk=pk_group)