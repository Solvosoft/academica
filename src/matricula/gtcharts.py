from django.db.models import Count, Q
from django.db.models.functions import Upper
from djgentelella.chartjs import VerticalBarChart
from djgentelella.groute import register_lookups

from matricula.models import Course, Enroll
from membership_core.gtcharts import BaseChart


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

@register_lookups(prefix="totalestmatriculados", basename="totalestmatriculados")
class EnrollStudentsReport(BaseChart, VerticalBarChart):
    def get_enrolls_completed(self):
        queryset = Enroll.objects.all().order_by('student').annotate(
            enrrols_count=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True)),
            enrolledstudents=Count('group__enroll', filter=Q(group__enroll__enroll_finished=True))
        ).values('student', 'enrrols_count', 'enrolledstudents')

        return queryset


    def get_labels(self):
        return [' Total de estudiantes matriculados']

    def get_datasets(self):
        self.index=0
        dataset = []
        students = self.get_enrolls_completed()
        for student in students:
            dataset.append(
                {'label': student['student'],
                 'backgroundColor': self.get_color(),
                 'borderColor': self.get_color(),
                 'borderWidth': 1,
                 'data': [student['enrrols_count'], student['enrolledstudents']]
                 },
            )
        return dataset


    def get_title(self):
        return {'display': True,
                'text': 'Total de personas matriculadas'
                }