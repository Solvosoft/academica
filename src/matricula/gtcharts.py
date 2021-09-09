from django.db.models import Count, Q
from django.db.models.functions import Upper
from django.utils.translation import gettext as _
from djgentelella.chartjs import VerticalBarChart
from djgentelella.groute import register_lookups

from matricula.models import Course, Enroll, Student
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
        return ['Desertaron']

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


@register_lookups(prefix="organitations_per_country", basename="organitations_per_country")
class OrganitationsPerCountryReport(BaseChart, VerticalBarChart):
    def get_organizations_per_country(self):
        queryset = Country.objects.filter(
                   student__organization__isnull= False
        ).exclude(student__organization=''
        ).values('pk', 'student__organization')

        country_dict = {}

        for country in Country.objects.filter(student__organization__isnull= False):
            country_dict['p_%d'%country.pk]=  Count('pk', filter=Q(pk=country.pk))
            queryset.aggregate(**country_dict)
        return queryset

    def get_labels(self):
        return ['Organizaciones por país']

    def get_datasets(self):
        self.index=0
        dataset = []
        organizations = self.get_organizations_per_country()
        for countries in organizations:
            dataset.append(
                {'label': countries['student__organization'],
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [countries['pk']]
                 },
            )
        return dataset


    def get_title(self):
        return {'display': True,
                'text': 'Reporte de organizaciones por país'
                }