from django.db.models import Count, Q
from django.db.models.functions import Upper
from djgentelella.chartjs import VerticalBarChart, PieChart
from djgentelella.groute import register_lookups

from matricula.models import Course, Enroll, Student, Period
from membership_core.gtcharts import BaseChart
from membership_core.models import Country


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
                 },
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
        self.countries = Student.objects.filter(enroll__enroll_activate=True).annotate(
            num_appearances=Count('country_id')
        ).values('country_id__name', 'num_appearances')

        super().__init__(*args, **kwargs)

    def get_labels(self):
        labels = []
        for country in self.countries:
            labels.append(
                country['country_id__name'],
            )

        return labels

    def get_datasets(self):
        self.index=0
        dataset = []
        country_data = []
        colors = []
        for country in self.countries:
            country_data.append(country['num_appearances'])
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
    def get_organizations_per_country(self):
        qp = Country.objects.filter(
                   student__organization__isnull= False
        ).exclude(student__organization=''
        ).values('pk', 'student__organization')

        country_dict = {}
        
        for country in Country.objects.filter(student__organization__isnull= False):
            country_dict[country.name]=  Count('pk', filter=Q(pk=country.pk))

        queryset = qp.aggregate(**country_dict)
        return queryset

    def get_labels(self):
        return ['Organizaciones por país']

    def get_datasets(self):
        self.index=0
        dataset = []
        organizations = self.get_organizations_per_country()
        for countries in organizations:
            dataset.append(
                {'label': countries,
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [organizations[countries]]
                 },
            )
        return dataset

    def get_title(self):
        return {'display': True,
                'text': 'Reporte de organizaciones por país'
                }


@register_lookups(prefix="total_courses_by_year", basename="total_courses_by_year")
class TotalCoursesByYear(BaseChart, VerticalBarChart):
    def get_years(self):
        queryset = Period.objects.filter(group__enroll__enroll_activate=True).order_by('start_date').values('start_date')

        years = {}
        for date in queryset:
            val = date['start_date'].strftime('%Y')
            if val in years:
                years[val] += 1
            else:
                years[val] = 1

        return years

    def get_labels(self):
        return ['Año correspondiente al curso']

    def get_datasets(self):
        self.index=0
        dataset = []
        years = self.get_years()
        for year, val in years.items():
            dataset.append(
                {'label': year,
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [val]
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
                'text': 'Reporte total de cursos por año'
                }


@register_lookups(prefix="total_courses_by_month", basename="total_courses_by_month")
class TotalCoursesByMonth(BaseChart, VerticalBarChart):
    def get_months(self):
        queryset = Period.objects.filter(group__enroll__enroll_activate=True).values('start_date')

        months = {}
        for date in queryset:
            val = date['start_date'].strftime('%m')
            if val in months:
                months[val] += 1
            else:
                months[val] = 1

        return months

    def get_labels(self):
        return ['Mes correspondiente al curso']

    def get_datasets(self):
        self.index = 0
        dataset = []
        dic_months = {
            '01': 'Enero',
            '02': 'Febrero',
            '03': 'Marzo',
            '04': 'Abril',
            '05': 'Mayo',
            '06': 'Junio',
            '07': 'Julio',
            '08': 'Agosto',
            '09': 'Septiembre',
            '10': 'Octubre',
            '11': 'Noviembre',
            '12': 'Diciembre',
        }
        months = self.get_months()
        for month, val in months.items():
            dataset.append(
                {
                    'label': dic_months[month],
                    'backgroundColor': self.get_color(),
                    'borderColor': self.get_color(),
                    'borderWidth': 1,
                    'data': [val]
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
                'text': 'Reporte total de cursos por mes'
        }
