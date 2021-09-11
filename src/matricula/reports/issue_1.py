from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse


@permission_required('matricula.view_reports')
def total_courses_by_year_report(request):
    context = {
         'graph_url': reverse('total_courses_by_year-list')
    }
    return render(request, 'reports/total_courses_by_year.html', context=context)


@permission_required('matricula.view_reports')
def total_courses_by_month_report(request):
    context = {
         'graph_url': reverse('total_courses_by_month-list')
    }
    return render(request, 'reports/total_courses_by_month.html', context=context)