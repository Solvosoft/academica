from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse


@permission_required('matricula.view_reports')
def approved_student_report(request):
    context = {
         'graph_url': reverse('approvedstudentreport-list')
    }
    return render(request, 'reports/approved_student_report.html', context=context)
