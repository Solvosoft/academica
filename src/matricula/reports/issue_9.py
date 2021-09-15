from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse


@permission_required('matricula.view_reports')
def student_by_organization_report(request):
    context = {
         'graph_url': reverse('student_by_org_report-list')
    }
    return render(request, 'reports/student_by_organization_report.html', context=context)
