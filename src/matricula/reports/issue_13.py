from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse


@permission_required('matricula.view_reports')
def organizations_per_country_report(request):
    context = {
         'graph_url': reverse('organitations_per_country-list')
    }
    return render(request, 'reports/organizations_per_country_report.html', context=context)