from django.db.models import Count, Q, Func, F
from django.utils.text import slugify
from djgentelella.chartjs import VerticalBarChart, PieChart
from djgentelella.groute import register_lookups

from matricula.forms import CourseGraphForm, CourseWithCoursefilterGraphForm, GroupSearchForm
from matricula.models import Course, Student, Group, Period
from matricula.utils import organization_names, get_label_months
from matricula.views.utils import get_active_period
from membership_core.gtcharts import BaseChart
from membership_core.models import Country
import json


@register_lookups(prefix="consolidadoestcurso", basename="consolidadoestcurso")
class ConsolidadoEstadisticasCurso(BaseChart, VerticalBarChart):
    def get_courses(self):
        queryset = Course.objects.all().order_by('name')
        period = self.request.GET.get('form_period', None)
        if period:
            queryset = queryset.filter(group__period=period)
        form = CourseWithCoursefilterGraphForm(self.request.GET)
        if form.is_valid():
            queryset= form.filter_queryset(queryset)
        return queryset.annotate(
            approve_count=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True,
                    group__enroll__go_to_one_class=True,
                    group__enroll__course_status = """approved""" )),
            uncomplete=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True,
                    group__enroll__go_to_one_class=True,
                    group__enroll__course_status= """uncomplete""")),
            reproved=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True,
                    group__enroll__go_to_one_class=True,
                    group__enroll__course_status= """reproved""")),
            withoutlessons=Count('group__enroll', filter=Q(group__enroll__enroll_finished=True,
                                                           group__enroll__go_to_one_class=False))
        ).values('name', 'approve_count', 'reproved','uncomplete', 'withoutlessons')

    def get_labels(self):
        return ['Aprobaron','Reprobaron', 'No Siguieron', 'Nunca Ingresaron']

    def get_datasets(self):
        self.index=0
        dataset = []
        courses = self.get_courses()
        for course in courses:
            dataset.append(
                {'label': course['name'],
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [course['approve_count'], course['reproved'], course['uncomplete'], course['withoutlessons']]
                 }
            )
        return dataset

    def get_scales(self):
        return {'yAxes': [{
                    'ticks': {
                        'suggestedMin': 0,  # minimum will be 0, unless there is a lower value.
                        'beginAtZero': True  # minimum value will be 0.
                    }
            }]
        }

    def get_title(self):
        return {'display': True,
                'text': 'Consolidado de estadísticas por curso'
                }


@register_lookups(prefix="uncompleted_student", basename="uncompleted_student")
class UncompletedStudentReport(BaseChart, VerticalBarChart):

    def get_courses(self):
        queryset = Course.objects.all()
        period = self.request.GET.get('form_period', None)
        if period:
            queryset = queryset.filter(group__period=period)
        else:
            queryset = queryset.filter(group__period__in=get_active_period())
        queryset = queryset.order_by('name').annotate(
            uncomplete=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True,
                    group__enroll__go_to_one_class=True,
                    group__enroll__course_status= """uncompleted"""), distinct=True)
        )
        form = CourseWithCoursefilterGraphForm(self.request.GET)
        if form.is_valid():
            queryset = form.filter_queryset(queryset)
        return queryset.values('name','uncomplete')

    def get_labels(self):
        return ['Estudiantes que no siguieron el curso']

    def get_datasets(self):
        self.index=0
        dataset = []
        courses = self.get_courses()
        for course in courses:
            dataset.append(
                {'label': course['name'],
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [course['uncomplete']]
                 },
            )
        return dataset

    def get_scales(self):
        return {'yAxes': [{
                    'ticks': {
                        'suggestedMin': 0,  # minimum will be 0, unless there is a lower value.
                        'beginAtZero': True  # minimum value will be 0.
                    }
            }]
        }

    def get_title(self):
        return {'display': True,
                'text': 'Reporte de estudiantes que no siguieron por curso'
                }


@register_lookups(prefix="totalestmatriculados", basename="totalestmatriculados")
class EnrollStudentsReport(BaseChart, VerticalBarChart):
    def get_enrolls_completed(self):
        queryset = Course.objects.all().order_by('name').annotate(
            enrrols_count=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True))
        ).values('name', 'enrrols_count')
        period = self.request.GET.get('form_period')
        if period:
            queryset = queryset.filter(group__period=period)
        form = CourseWithCoursefilterGraphForm(self.request.GET)
        if form.is_valid():
            queryset= form.filter_queryset(queryset)
        return queryset

    def get_scales(self):
        return {'yAxes': [{
                    'ticks': {
                        'suggestedMin': 0, # minimum will be 0, unless there is a lower value.
                        'beginAtZero': True # minimum value will be 0.
                    }
            }]
        }

    def get_labels(self):
        return [' Total de estudiantes matriculados']

    def get_datasets(self):
        self.index=0
        dataset = []
        students = self.get_enrolls_completed()
        for student in students:
            dataset.append(
                {'label': student['name'],
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [student['enrrols_count']]
                 },
            )
        return dataset


    def get_title(self):
        return {'display': True,
                'text': 'Reporte del total de personas matriculadas'
                }


@register_lookups(prefix="approvedstudentreport", basename="approvedstudentreport")
class ApprovedStudentReport(BaseChart, VerticalBarChart):

    def get_courses(self):
        queryset = Course.objects.all()
        period = self.request.GET.get('form_period', None)
        if period:
            queryset = queryset.filter(group__period=period)
        else:
            queryset = queryset.filter(group__period__in=get_active_period())
        queryset = queryset.order_by('name').annotate(
            approve_count=Count('group__enroll', filter=Q(
                group__enroll__enroll_finished=True,
                group__enroll__go_to_one_class=True,
                group__enroll__course_status="""approved"""), distinct=True)).values('name', 'approve_count')
        form = CourseWithCoursefilterGraphForm(self.request.GET)
        if form.is_valid():
            queryset= form.filter_queryset(queryset)
        return queryset

    def get_labels(self):
        return ['Aprobaron']

    def get_datasets(self):
        self.index = 0
        dataset = []
        courses = self.get_courses()
        for course in courses:
            dataset.append(
                {'label': course['name'],
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [course['approve_count']]
                 },
            )
        return dataset

    def get_title(self):
        return {'display': True,
            'text': 'Total de estudiantes aprobados por curso'}

    def get_scales(self):
        return {'yAxes': [{
                    'ticks': {
                        'suggestedMin': 0, # minimum will be 0, unless there is a lower value.
                        'beginAtZero': True # minimum value will be 0.
                    }
            }]
        }

@register_lookups(prefix="reprovedstudentreport", basename="reprovedstudentreport")
class ReprovedStudentReport(BaseChart, VerticalBarChart):

    def get_courses(self):
        queryset = Course.objects.all()
        period = self.request.GET.get('form_period', None)
        if period:
            queryset = queryset.filter(group__period=period)
        else:
            queryset = queryset.filter(group__period__in=get_active_period())

        queryset = queryset.order_by('name').annotate(
            reprove_count=Count('group__enroll', filter=Q(
                group__enroll__enroll_finished=True,
                group__enroll__go_to_one_class=True,
                group__enroll__course_status="""reproved"""), distinct=True)).values('name', 'reprove_count')
        form = CourseWithCoursefilterGraphForm(self.request.GET)
        if form.is_valid():
            queryset= form.filter_queryset(queryset)
        return queryset

    def get_labels(self):
        return ['Reprobaron']

    def get_datasets(self):
        self.index = 0
        dataset = []
        courses = self.get_courses()
        for course in courses:
            dataset.append(
                {'label': course['name'],
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [course['reprove_count']]
                 },
            )
        return dataset

    def get_title(self):
        return {'display': True,
            'text': 'Total de estudiantes reprobados por curso'}

    def get_scales(self):
        return {'yAxes': [{
                    'ticks': {
                        'suggestedMin': 0, # minimum will be 0, unless there is a lower value.
                        'beginAtZero': True # minimum value will be 0.
                    }
            }]
        }

@register_lookups(prefix="student_without_lessons_report", basename="student_without_lessons_report")
class NeverAttendStudentReport(BaseChart, VerticalBarChart):

    def get_courses(self):

        queryset = Course.objects.all()
        period = self.request.GET.get('form_period', None)
        if period:
            queryset = queryset.filter(group__period=period)
        else:
            queryset = queryset.filter(group__period__in=get_active_period())


        queryset = queryset.order_by('name').annotate(
            withoutlessons=Count('group__enroll', filter=Q(group__enroll__enroll_finished=True,
                                                           group__enroll__go_to_one_class=False), distinct=True)
        ).values('name', 'withoutlessons')
        period = self.request.GET.get('form_period', None)
        if period:
            queryset = queryset.filter(group__period=period)
        form = CourseWithCoursefilterGraphForm(self.request.GET)
        if form.is_valid():
            queryset= form.filter_queryset(queryset)
        return queryset

    def get_labels(self):
        return ['Nunca asistieron a clases']

    def get_datasets(self):
        self.index = 0
        dataset = []
        courses = self.get_courses()
        for course in courses:
            dataset.append(
                {'label': course['name'],
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [course['withoutlessons']],
                },
            )
        return dataset

    def get_scales(self):
        return {'yAxes': [{
                    'ticks': {
                        'suggestedMin': 0, # minimum will be 0, unless there is a lower value.
                        'beginAtZero': True # minimum value will be 0.
                    }
            }]
        }

    def get_title(self):
        return {'display': True,
                'text': 'Reporte de estudiantes que nunca ingresaron a los cursos'
                }


@register_lookups(prefix="countries_in_courses", basename="countries_in_courses")
class CountriesInCoursesReport(BaseChart, PieChart):

    def __init__(self, *args, **kwargs):
        self.countries = Country.objects.all().annotate(
            num_appearances=Count('student', filter=Q(student__enroll__enroll_activate=True))
        ).filter(num_appearances__gt=0)
        self._countries=None
        super().__init__(*args, **kwargs)

    def get_labels(self):
        labels = []
        for country in self.filter_countries():
            labels.append("%s (%d)"%(country.name, country.num_appearances))

        return labels

    def filter_countries(self):
        form = CourseGraphForm(self.request.GET)
        form.is_valid()
        filters = {}
        periods = Period.objects.all()
        if 'period' in form.cleaned_data and form.cleaned_data['period']:
            if form.cleaned_data['period']:
                filters['student__enroll__group__period__in'] = periods.filter(finish_date__year__in=form.cleaned_data['period'])
        else:
            filters['student__enroll__group__period__in'] = get_active_period()
        if 'workload' in form.cleaned_data and form.cleaned_data['workload']:
            filters['student__enroll__group__duration_hours__in'] = form.cleaned_data['workload']
        if self._countries is None:
            self._countries = Country.objects.all().annotate(
                num_appearances=Count('student', filter=Q(student__enroll__enroll_activate=True, **filters))
            ).filter(num_appearances__gt=0)
            self.countries = self._countries
        return self.countries

    def get_datasets(self):

        self.index=0
        dataset = []
        country_data = []
        colors = []
        for country in self.filter_countries():
            country_data.append(country.num_appearances)
            colors.append(self.get_color())

        dataset.append(
            {'label': 'Country',
             'data': country_data,
             'backgroundColor': colors,
             },
        )

        return dataset

    def get_title(self):
        return {'display': True,
                'text': 'Reporte de países los cuales participan en los cursos'
                }


def update_organizations(countries):
    delete_countries=[]
    for country in countries:
        countries[country]['count']=len(countries[country]['orgs'])
        if not countries[country]['count']:
            delete_countries.append(country)
    for delcountry in delete_countries:
        del countries[delcountry]
    return countries

def get_organizations_per_country(countries_list, extras={}):

    countries = {}
    for country in countries_list:
        countries[country['id']] = {
            'name': country['name'],
            'orgs': [],
            'count': 0
        }
    queryset=Student.objects.all()
    if extras:
        queryset = queryset.filter(**extras)
    orgs = queryset.exclude(organization='').values('organization', 'country').distinct()

    for org in orgs:
        if org['country'] not in countries:
            continue
        for name in organization_names(org["organization"]):
            if name.lower() not in countries[org['country']]['orgs']:
                countries[org['country']]['orgs'].append(name.lower())

    return update_organizations(countries)


@register_lookups(prefix="organitations_per_country", basename="organitations_per_country")
class OrganitationsPerCountryReport(BaseChart, PieChart):
    def __init__(self, *args, **kwargs):
        self.countries = Country.objects.all().annotate(
            num_appearances=Count('student', filter=Q(student__enroll__enroll_activate=True))
        ).filter(num_appearances__gt=0).values('id', 'name')
        super().__init__(*args, **kwargs)

    def get_organizations_per_country(self):
        form = CourseGraphForm(self.request.GET)
        form.is_valid()
        filters = {}
        periods = Period.objects.all()
        if 'period' in form.cleaned_data and form.cleaned_data['period']:
            if form.cleaned_data['period']:
                filters['enroll__group__period__in'] = periods.filter(finish_date__year__in=form.cleaned_data['period'])
        else:
            filters['enroll__group__period__in'] = get_active_period()
        if 'workload' in form.cleaned_data and form.cleaned_data['workload']:
            filters['enroll__group__duration_hours__in'] = form.cleaned_data['workload']

        return get_organizations_per_country(self.countries, extras=filters)

    def get_labels(self):
        labels = []
        for country in self.countries:
            labels.append(country['name'])

        return labels

    def get_datasets(self):
        self.index=0
        dataset = []

        organizations = self.get_organizations_per_country()
        data = []
        colors = []
        for country in self.countries:
            if country['id'] in organizations:
                data.append(organizations[country['id']]['count'])
                colors.append(self.get_color())
        dataset.append(
                {'label': 'Cantidad de organizaciones',
                 'backgroundColor': colors,
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': data
                 },
            )
        return dataset

    def get_scales(self):
        return {'yAxes': [{
                    'ticks': {
                        'suggestedMin': 0, 
                        'beginAtZero': True 
                    }
            }]
        }

    def get_title(self):
        return {'display': True,
                'text': 'Reporte de organizaciones por país'
                }


@register_lookups(prefix="total_courses_by_year", basename="total_courses_by_year")
class TotalCoursesByYear(BaseChart, VerticalBarChart):
    def get_years(self):
        form = CourseGraphForm(self.request.GET)
        groups = Group.objects.all()
        form_isvalid = form.is_valid()
        if form_isvalid:
            if form.cleaned_data['period']:
                groups = groups.filter(period__finish_date__year__in=form.cleaned_data['period'])
        years = groups.dates('period__finish_date', 'year')
        yearparams ={str(x.year) : Count('pk', filter=Q(period__finish_date__year=x.year)) for x in years }
        queryset = Group.objects.all()
        if form_isvalid:
            queryset = form.filter_queryset(queryset)
        return queryset.aggregate(**yearparams)

    def get_labels(self):
        return ['Año correspondiente al curso']

    def sort_years(self, years):
        years = list(map(lambda x: int(x), years))
        years.sort()
        return years

    def get_datasets(self):
        self.index=0
        dataset = []
        years=dict(self.get_years())
        yearskeys = self.sort_years(years.keys())
        for yearkey in yearskeys:
            dataset.append(
                {'label': str(yearkey),
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [years[str(yearkey)]]
                 },
            )
        return dataset

    def get_scales(self):
        return {'yAxes': [{
                'ticks': {
                    'suggestedMin': 0,  # minimum will be 0, unless there is a lower value.
                    'beginAtZero': True  # minimum value will be 0.
                }
            }]
        }

    def get_title(self):
        return {'display': False,
                'text': 'Reporte total de cursos por año'
                }


@register_lookups(prefix="total_courses_by_month", basename="total_courses_by_month")
class TotalCoursesByMonth(BaseChart, VerticalBarChart):
    def get_months(self):
        months = Group.objects.dates('enroll_finish', 'month')
        monthsparams ={str(x.month) : Count('pk', filter=Q(enroll_finish__month=x.month)) for x in months }
        form = CourseGraphForm(self.request.GET)
        queryset = Group.objects.all()
        if form.is_valid():
            queryset = form.filter_queryset(queryset)
        return queryset.aggregate(**monthsparams)

    def sort_months(self, months):
        months = list(map(lambda x: int(x), months))
        months.sort()
        return months

    def get_labels(self):
        return ['Mes correspondiente al curso']

    def get_datasets(self):
        self.index = 0
        dataset = []


        months=dict(self.get_months())
        monthskeys = self.sort_months(months.keys())
        for month in monthskeys:
            dataset.append(
                {
                    'label': get_label_months(month),
                    'backgroundColor': self.get_color(),
                    'borderColor': self.get_color(),
                    'borderWidth': 1,
                    'data': [months[str(month)]]
                },
            )
        return dataset

    def get_scales(self):
        return {'yAxes': [{
                    'ticks': {
                        'suggestedMin': 0,  # minimum will be 0, unless there is a lower value.
                        'beginAtZero': True  # minimum value will be 0.
                    }
            }]
        }

    def get_title(self):
        return {'display': False,
                'text': 'Reporte total de cursos por mes'
        }

@register_lookups(prefix="student_by_org_report", basename="student_by_org_report")
class StudentByOrganizationReport(BaseChart, VerticalBarChart):
    def get_organizations(self):
        orgsname=[]
        orgs = Student.objects.exclude(organization='').values('organization', 'country').distinct()
        for org in orgs:
            for name in organization_names(org["organization"]):
                if name.lower() not in orgsname:
                    orgsname.append(name.lower())

        return orgsname

    def get_students(self):
        orgs = self.get_organizations()
        queryset=Student.objects.filter(enroll__enroll_finished=True)
        queryparams = {}
        for org in orgs:
            queryparams[slugify(org)] = Count('pk', filter=Q(organization__icontains=org))

        queryset=queryset.aggregate(**queryparams)

        orga_dict = {}
        for org in orgs:
            orga_dict[org]=queryset[slugify(org)]

        return orga_dict

    def get_labels(self):

        return ['Cantidad de estudiantes por organización']

    def get_datasets(self):
        self.index = 0
        dataset = []
        students = self.get_students()

        for stud, val in students.items():
            dataset.append(
                {'label': stud.title(),
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [val]
                 },
        )
        return dataset

    def get_title(self):
        return {'display': True,
            'text': 'Total de estudiantes matriculados por organización'}

    def get_scales(self):
        return {'yAxes': [{
            'ticks': {
                'suggestedMin': 0,  # minimum will be 0, unless there is a lower value.
                'beginAtZero': True  # minimum value will be 0.
            }
        }]
        }

