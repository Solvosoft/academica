from django.db.models import Count, Q, Func, F
from django.utils.text import slugify
from djgentelella.chartjs import VerticalBarChart, PieChart
from djgentelella.groute import register_lookups

from matricula.models import Course, Student, Group
from matricula.utils import get_label_months
from membership_core.gtcharts import BaseChart
from membership_core.models import Country
import json


@register_lookups(prefix="consolidadoestcurso", basename="consolidadoestcurso")
class ConsolidadoEstadisticasCurso(BaseChart, VerticalBarChart):
    def get_courses(self):
        queryset = Course.objects.all().order_by('name').annotate(
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
        period = self.request.GET.get('period', None)
        if period:
            queryset = queryset.filter(group__period=period)
        return queryset

    def get_labels(self):
        return ['Aprobaron','Reprobaron', 'Desertaron', 'Nunca Ingresaron']

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



    def get_title(self):
        return {'display': True,
                'text': 'Consolidado de estadísticas por curso'
                }


@register_lookups(prefix="uncompleted_student", basename="uncompleted_student")
class UncompletedStudentReport(BaseChart, VerticalBarChart):

    def get_courses(self):
        queryset = Course.objects.all().order_by('name').annotate(
            uncomplete=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True,
                    group__enroll__go_to_one_class=True,
                    group__enroll__course_status= """uncomplete"""))
        ).values('name','uncomplete')
        period = self.request.GET.get('period', None)
        if period:
            queryset = queryset.filter(group__period=period)
        return queryset

    def get_labels(self):
        return ['Estudiantes que desertaron cursos']

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
                'text': 'Reporte de estudiantes que desertaron por curso'
                }


@register_lookups(prefix="totalestmatriculados", basename="totalestmatriculados")
class EnrollStudentsReport(BaseChart, VerticalBarChart):
    def get_enrolls_completed(self):
        queryset = Course.objects.all().order_by('name').annotate(
            enrrols_count=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True))
        ).values('name', 'enrrols_count')
        period = self.request.GET.get('period', None)
        if period:
            queryset = queryset.filter(group__period=period)
        return queryset


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
        queryset = Course.objects.all().order_by('name').annotate(
            approve_count=Count('group__enroll', filter=Q(
                group__enroll__enroll_finished=True,
                group__enroll__go_to_one_class=True,
                group__enroll__course_status="""approved"""))).values('name', 'approve_count')

        period = self.request.GET.get('period', None)
        if period:
            queryset = queryset.filter(group__period=period)
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


@register_lookups(prefix="student_without_lessons_report", basename="student_without_lessons_report")
class NeverAttendStudentReport(BaseChart, VerticalBarChart):

    def get_courses(self):
        queryset = Course.objects.all().order_by('name').annotate(
            withoutlessons=Count('group__enroll', filter=Q(group__enroll__enroll_finished=True,
                                                           group__enroll__go_to_one_class=False))
        ).values('name', 'withoutlessons')
        period = self.request.GET.get('period', None)
        if period:
            queryset = queryset.filter(group__period=period)
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
        super().__init__(*args, **kwargs)

    def get_labels(self):
        labels = []
        for country in self.countries:
            labels.append("%s (%d)"%(country.name, country.num_appearances))

        return labels

    def get_datasets(self):

        self.index=0
        dataset = []
        country_data = []
        colors = []
        for country in self.countries:
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

@register_lookups(prefix="organitations_per_country", basename="organitations_per_country")
class OrganitationsPerCountryReport(BaseChart, VerticalBarChart):

    def update_organizations(self, countries):
        delete_countries=[]
        for country in countries:
            countries[country]['count']=len(countries[country]['orgs'])
            if not countries[country]['count']:
                delete_countries.append(country)
        for delcountry in delete_countries:
            del countries[delcountry]
        return countries

    def get_organizations_per_country(self):
        countriesquery = Country.objects.filter(student__isnull=False).distinct().values('id', 'name')
        countries = {}
        for country in countriesquery:
            countries[country['id']] = {
                'name': country['name'],
                'orgs': [],
                'count': 0
            }
        orgs = Student.objects.exclude(organization='').values('organization', 'country').distinct()
        for org in orgs:
            try:
                for value in json.loads(org["organization"]):
                    if value['value'].lower() not in countries[org['country']]['orgs']:
                        countries[org['country']]['orgs'].append(value['value'].lower())
            except json.decoder.JSONDecodeError as e:
                if org["organization"].lower() not in countries[org['country']]['orgs']:
                    countries[org['country']]['orgs'].append(org["organization"].lower())

        return self.update_organizations(countries)

    def get_labels(self):
        return ['Organizaciones por país']

    def get_datasets(self):
        self.index=0
        dataset = []

        organizations = self.get_organizations_per_country()
        for countries in organizations.values():
            dataset.append(
                {'label': countries['name'],
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [countries['count']]
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
        years = Group.objects.dates('period__finish_date', 'year')
        yearparams ={str(x.year) : Count('pk', filter=Q(period__finish_date__year=x.year)) for x in years }
        return Group.objects.aggregate(**yearparams)

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
        return Group.objects.aggregate(**monthsparams)

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
            try:
                for value in json.loads(org["organization"]):
                    if value['value'].lower() not in orgsname:
                        orgsname.append(value['value'].lower())
            except json.decoder.JSONDecodeError as e:
                if org["organization"].lower() not in orgsname:
                    orgsname.append(org["organization"].lower())

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

