from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse


@permission_required('matricula.view_reports')
def student_without_lessons_report(request):
    context = {
         'graph_url': reverse('student_without_lessons_report-list')
    }
    return render(request, 'reports/students_without_lessons_report.html', context=context)
