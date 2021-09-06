from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse


@permission_required('matricula.view_reports')
def uncompleted_student_report(request):
    context = {
         'graph_url': reverse('uncompleted_student-list')
    }
    return render(request, 'reports/uncompleted_student_report.html', context=context)
