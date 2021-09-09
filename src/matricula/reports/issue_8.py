from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse


@permission_required('matricula.view_reports')
def countries_in_courses_report(request):
    context = {
         'graph_url': reverse('countries_in_courses-list')
    }
    return render(request, 'reports/countries_in_courses_report.html', context=context)