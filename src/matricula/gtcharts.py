from django.db.models import Count, Q
from djgentelella.chartjs import VerticalBarChart
from djgentelella.groute import register_lookups

from matricula.models import Course
from membership_core.gtcharts import BaseChart


@register_lookups(prefix="consolidadoestcurso", basename="consolidadoestcurso")
class ConsolidadoEstadisticasCurso(BaseChart, VerticalBarChart):
    def get_courses(self):
        queryset = Course.objects.all().annotate(
            approve_count=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True,
                    group__enroll__course_status = 'approved'                                                                    'group__enrollment__enroll_finished'
                )),
            uncomplete=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True,
                    group__enroll__course_status= "uncomplete"                                                                       'group__enrollment__enroll_finished'
                )),
            withoutlessons=Count('group__enroll', filter=Q(
            group__enroll__enroll_finished=True,
            group__enroll__go_to_one_class=False,
            ))
        ).values('name', 'approve_count', 'uncomplete', 'withoutlessons')

        return queryset


    def get_labels(self):
        return ['Aprobaron', 'Desertaron', 'Nunca Ingresaron']

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
                 'data': [course['approve_count'], course['uncomplete'], course['withoutlessons']]
                 },
            )
        return dataset



    def get_title(self):
        return {'display': True,
                'text': 'Consolidado de estadísticas por curso'
                }
