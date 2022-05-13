import json
from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.text import slugify
from matricula.forms import CourseGraphForm, CourseWithCoursefilterGraphForm, CourseTableForm, CountryForm
from matricula.gtcharts import OrganitationsPerCountryReport, get_organizations_per_country
from matricula.models import Student, Period, Course
from matricula.serializers import GroupSerializer
from matricula.views.utils import get_active_period
from membership_core.models import Country


@permission_required('matricula.view_reports')
def total_courses_by_year_report(request):
    form = CourseGraphForm(request.GET)
    form.is_valid()
    context = {
         'title': 'Total de cursos por año',
         'form': form,
         'graph_url': reverse('total_courses_by_year-list')+ '?'+form.get_urlencode(),

    }
    return render(request, 'reports/generic_chart_with_form.html', context=context)

@permission_required('matricula.view_reports')
def total_courses_by_month_report(request):
    form = CourseGraphForm(request.GET)
    form.is_valid()
    context = {
        'title': 'Total de cursos por mes',
         'form': form,
         'graph_url': reverse('total_courses_by_month-list') + '?'+form.get_urlencode(),
    }
    return render(request, 'reports/generic_chart_with_form.html', context=context)


@permission_required('matricula.view_reports')
def course_topics_report(request):
    form = CourseTableForm(request.GET)
    form.is_valid()
    context = {
        'form': form,
        'url': reverse('course_topics_api-list'),
        'title': 'Temas de los cursos que se han impartido en la Upo en total, por año o por mes.'
    }
    return render(request, 'reports/course_topics_report.html', context=context)


@permission_required('matricula.view_reports')
def enrolls_report(request):

    form = CourseWithCoursefilterGraphForm(request.GET)
    form.is_valid()
    periods = Period.objects.all()
    if 'all_period' in form.cleaned_data and form.cleaned_data['all_period']:
        if form.cleaned_data['period']:
            periods = periods.filter(finish_date__year__in=form.cleaned_data['period'])
    else:
        periods= get_active_period()
    period_list =[]
    form.cleaned_data.pop('period')
    urlsparams = form.get_urlencode()
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('totalestmatriculados-list')+"?form_period=%d%s"%(period.pk, urlsparams)
        })
    context = {
        'form': form,
        'periods': period_list,
        'title': 'Total de personas matriculadas'
    }
    return render(request, 'reports/standard_period_report.html', context=context)


@permission_required('matricula.view_reports')
def approved_student_report(request):
    form = CourseWithCoursefilterGraphForm(request.GET)
    form.is_valid()
    periods = Period.objects.all()
    urlsparams=form.get_urlencode()
    if 'all_period' in form.cleaned_data and form.cleaned_data['all_period']:
        if form.cleaned_data['period']:
            periods = periods.filter(finish_date__year__in=form.cleaned_data['period'])
    else:
        periods = get_active_period()
    period_list = []
    form.cleaned_data.pop('period')
    urlsparams = form.get_urlencode()
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('reprovedstudentreport-list')+"?form_period=%d%s"%(period.pk, urlsparams)
        })
    context = {
        'form': form,
         'periods': period_list,
         'title': 'Total de estudiantes aprobados por curso'
    }
    return render(request, 'reports/standard_period_report.html', context=context)

@permission_required('matricula.view_reports')
def reproved_student_report(request):
    form = CourseWithCoursefilterGraphForm(request.GET)
    form.is_valid()
    periods = Period.objects.all()
    urlsparams=form.get_urlencode()
    if 'all_period' in form.cleaned_data and form.cleaned_data['all_period']:
        if form.cleaned_data['period']:
            periods = periods.filter(finish_date__year__in=form.cleaned_data['period'])
    else:
        periods = get_active_period()
    period_list = []
    form.cleaned_data.pop('period')
    urlsparams = form.get_urlencode()
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('reprovedstudentreport-list')+"?form_period=%d%s"%(period.pk, urlsparams)
        })
    context = {
        'form': form,
         'periods': period_list,
         'title': 'Total de estudiantes reprobados por curso'
    }
    return render(request, 'reports/standard_period_report.html', context=context)

@permission_required('matricula.view_reports')
def uncompleted_student_report(request):
    form = CourseWithCoursefilterGraphForm(request.GET)
    form.is_valid()
    periods = Period.objects.all()
    if 'all_period' in form.cleaned_data and form.cleaned_data['all_period']:
        if form.cleaned_data['period']:
            periods = periods.filter(finish_date__year__in=form.cleaned_data['period'])
    else:
        periods = get_active_period()
    period_list = []
    form.cleaned_data.pop('period')
    urlsparams = form.get_urlencode()
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('uncompleted_student-list')+"?form_period=%d%s"%(period.pk, urlsparams)
        })
    context = {
        'form': form,
         'periods': period_list,
         'title': 'Estudiantes que no siguieron los cursos'
    }
    return render(request, 'reports/standard_period_report.html', context=context)


@permission_required('matricula.view_reports')
def student_without_lessons_report(request):
    form = CourseWithCoursefilterGraphForm(request.GET)
    form.is_valid()
    periods = Period.objects.all()
    if 'all_period' in form.cleaned_data and form.cleaned_data['all_period']:
        if form.cleaned_data['period']:
            periods = periods.filter(finish_date__year__in=form.cleaned_data['period'])
    else:
        periods = get_active_period()
    period_list = []
    form.cleaned_data.pop('period')
    urlsparams = form.get_urlencode()
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('student_without_lessons_report-list')+"?form_period=%d%s"%(period.pk, urlsparams)
        })
    context = {
        'form': form,
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
    form = CourseWithCoursefilterGraphForm(request.GET)
    form.is_valid()
    periods = Period.objects.all()
    if 'all_period' in form.cleaned_data and form.cleaned_data['all_period']:
        if form.cleaned_data['period']:
            periods = periods.filter(finish_date__year__in=form.cleaned_data['period'])
    else:
        periods = get_active_period()
    period_list = []
    form.cleaned_data.pop('period')
    urlsparams = form.get_urlencode()
    for period in periods:
        period_list.append({
            'title': str(period),
            'url': reverse('consolidadoestcurso-list')+"?form_period=%d%s"%(period.pk, urlsparams)
        })
    context = {
        'form': form,
        'periods': period_list,
        'title': "Estadísticas por curso"
    }
    return render(request, 'reports/standard_period_report.html', context=context)

@permission_required('matricula.view_reports')
def ranking_course_enrolls_view(request):
    form = CourseTableForm(request.GET)
    form.is_valid()
    context = {
        'form': form,
        "url": reverse('ranking_course_enrolls_api-list'),
        "title": "Ranking de cursos (personas matriculadas)"
    }
    return render(request, 'reports/ranking_course_enrolls.html', context=context)


@permission_required('matricula.view_reports')
def ranking_course_approved_view(request):
    form = CourseTableForm(request.GET)
    form.is_valid()
    context = {
        'form': form,
        "url": reverse('ranking_course_approved_api-list'),
        "title": "Ranking de cursos (personas aprobadas)"
    }

    return render(request, 'reports/ranking_course_approved.html', context=context)


def get_organization_by_countries(country):
    orgas_list = []
    orgs = Student.objects.filter(country__pk=country).exclude(organization='').values("organization")
    for org in orgs:
        try:
            for value in json.loads(org["organization"]):
                orgas_list.append(value['value'].lower())
        except json.decoder.JSONDecodeError as e:
            orgas_list.append(org["organization"].lower())

    return orgas_list

def add_count_student(organizations):
    aux_list = []

    for key, org_item in organizations.items():
        orga_country = get_organization_by_countries(key)
        for item in org_item['orgs']:
            aux_list.append({"org": item, "count": orga_country.count(item)})
        org_item['orgs'] = aux_list
        aux_list = []


@permission_required('matricula.view_reports')
def organizations_per_country_report(request):
    countries = Country.objects.all().annotate(
            num_appearances=Count('student', filter=Q(student__enroll__enroll_activate=True))
        ).filter(num_appearances__gt=0)

    id_list = list(countries.values_list('id', flat=True))
    organizations = get_organizations_per_country(countries.values('id', 'name'))
    add_count_student(organizations)

    context = {
         'countryform': CountryForm(countries=Country.objects.filter(pk__in=id_list)),
         'organizations': organizations,
         'graph_url': reverse('organitations_per_country-list'),
         'title': 'Cantidad de organizaciones por país'
    }
    return render(request, 'reports/organizations_per_country_report.html', context=context)


@permission_required('matricula.view_reports')
def ranking_group_enrolls(request, pk):

    course = get_object_or_404(Course, pk=pk)

    if course:
        groups = course.group_set.all()
        info = GroupSerializer(data=groups, many=True)
        info.is_valid()
        return JsonResponse({"result": "ok", "groups": info.data})
    return JsonResponse({"result": "error", "message": "Object doesn't exists"})