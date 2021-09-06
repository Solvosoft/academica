from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse


@permission_required('matricula.view_reports')
def enrolls_report(request):
    context = {
         'graph_url': reverse('totalestmatriculados-list')
    }
    return render(request, 'reports/enrolls_report.html', context=context)