import json

from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Q
from django.shortcuts import render
from django.urls import reverse
from django.utils.text import slugify

from matricula.models import Student
from matricula.views.utils import get_active_period


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


@permission_required('matricula.view_reports')
def course_topics_report(request):
    return render(request, 'reports/course_topics_report.html')


@permission_required('matricula.view_reports')
def enrolls_report(request):
    periods= get_active_period()
    period_list =[]
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('totalestmatriculados-list')+"?period=%d"%period.pk
        })
    context = {
         'periods': period_list,
        'title': 'Total de personas matriculadas'
    }
    return render(request, 'reports/standard_period_report.html', context=context)

@permission_required('matricula.view_reports')
def approved_student_report(request):

    periods= get_active_period()
    period_list =[]
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('approvedstudentreport-list')+"?period=%d"%period.pk
        })
    context = {
         'periods': period_list,
         'title': 'Total de estudiantes aprobados por curso'
    }
    return render(request, 'reports/standard_period_report.html', context=context)

@permission_required('matricula.view_reports')
def uncompleted_student_report(request):
    periods= get_active_period()
    period_list =[]
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('uncompleted_student-list')+"?period=%d"%period.pk
        })
    context = {
         'periods': period_list,
        'title': ''
    }
    return render(request, 'reports/standard_period_report.html', context=context)


@permission_required('matricula.view_reports')
def student_without_lessons_report(request):
    periods= get_active_period()
    period_list =[]
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('student_without_lessons_report-list')+"?period=%d"%period.pk
        })
    context = {
         'periods': period_list,
        'title': "Personas que nunca ingresaron a los cursos"
    }
    return render(request, 'reports/standard_period_report.html', context=context)


@permission_required('matricula.view_reports')
def countries_in_courses_report(request):
    context = {
         'graph_url': reverse('countries_in_courses-list'),
        'title': "Países de los cuales participan en los cursos"
    }
    return render(request, 'reports/countries_in_courses_report.html', context=context)

def get_organizations():
    orgsname=[]
    orgs = Student.objects.exclude(organization='').values('organization', 'country').distinct()
    for org in orgs:
        try:
            for value in json.loads(org["organization"]):
                if value['value'].lower() not in orgsname:
                    orgsname.append(value['value'].lower())
        except json.decoder.JSONDecodeError as e:
            if org["organization"].lower() not in orgsname:
                orgsname.append(org["organization"].lower())

    return orgsname

def get_students():
    orgs = get_organizations()
    queryset=Student.objects.all() #.filter(enroll__enroll_finished=True)
    queryparams = {}
    for org in orgs:
        if '"' in org:
            queryparams[slugify(org)] = Count('pk', filter=Q(organization__icontains=json.dumps(org)))
        else:
            queryparams[slugify(org)] = Count('pk', filter=Q(organization__icontains=org))
    queryset=queryset.aggregate(**queryparams)

    orga_dict = {}
    for org in orgs:
        orga_dict[org.title()]=queryset[slugify(org)]

    return orga_dict

@permission_required('matricula.view_reports')
def student_by_organization_report(request):

    context = {
         'students' : get_students(),
        'title': 'Participantes por organización'
    }
    return render(request, 'reports/student_by_organization_report.html', context=context)

@permission_required('matricula.view_reports')
def consolidado_estadisticas_cursos(request):
    context = {
         'graph_url': reverse('consolidadoestcurso-list')
    }
    periods= get_active_period()
    period_list =[]
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('consolidadoestcurso-list')+"?period=%d"%period.pk
        })
    context = {
         'periods': period_list,
        'title': "Estadísticas por curso"
    }
    return render(request, 'reports/standard_period_report.html', context=context)

@permission_required('matricula.view_reports')
def ranking_course_enrolls_view(request):
    context = {
        "title": "Ranking de cursos (personas matriculadas)"
    }
    return render(request, 'reports/ranking_course_enrolls.html', context=context)


@permission_required('matricula.view_reports')
def ranking_course_approved_view(request):
    context = {
        "title": "Ranking de cursos (personas aprobadas)"
    }
    return render(request, 'reports/ranking_course_approved.html', context=context)



@permission_required('matricula.view_reports')
def organizations_per_country_report(request):
    context = {
         'graph_url': reverse('organitations_per_country-list'),
         'title': 'Cantidad de organizaciones por país'
    }
    return render(request, 'reports/organizations_per_country_report.html', context=context)
















