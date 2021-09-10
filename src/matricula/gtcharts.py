import json

from django.db.models import Count, Q, Func, F, Exists, Sum
from django.db.models.functions import Upper
from djgentelella.chartjs import VerticalBarChart
from djgentelella.groute import register_lookups

from matricula.models import Course, Enroll, Student
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
        queryset = Enroll.objects.all().order_by('student').annotate(
            enrrols_count=Count('group__enroll', filter=Q(
                    group__enroll__enroll_finished = True))
        ).values('student', 'enrrols_count')

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


@register_lookups(prefix="student_by_org_report", basename="student_by_org_report")
class StudentByOrganizationReport(BaseChart, VerticalBarChart):

    def get_organizations(self):

        orgs = Student.objects.filter(enroll__enroll_finished=True, organization__isnull=False).exclude(organization='').annotate(
            org_lower=Func(F('organization'), function='LOWER')).values('org_lower').distinct()
        self.organizations = []
        str = '"value"'
        for item in orgs:
            if isinstance(item, dict):
                if 'org_lower' in item:
                    if str in item['org_lower']:
                        temp_org = list(item['org_lower'])
                        temp = temp_org[10:]
                        temp2 = temp[:-2]
                        org_str = ''.join(temp2)
                        self.organizations.append(org_str)
                    else:
                        self.organizations.append(item['org_lower'])
                else:
                    self.organizations.append(item)
            else:
                self.organizations.append(item)

        self.organizations = set(self.organizations)
        return self.organizations

    def get_students(self):

        '''org_dict = {}
        queryset = Student.objects.filter(enroll__enroll_finished=True, organization__isnull=False).exclude(organization='').annotate(
            org_lower=Func(F('organization'), function='LOWER')).values('org_lower').annotate(
            num=Count('org_lower')).values('org_lower', 'num')

        for value in queryset:
            if value['org_lower'] in org_dict:

                org_dict[value['org_lower']] += 1
            else:
                org_dict[value['org_lower']] = 1 '''

        orga_dict = {}
        for values in self.get_organizations():
            temp = Student.objects.filter(enroll__enroll_finished=True).filter(organization__iexact=values).count()
            if temp == 0:
                temp = Student.objects.filter(enroll__enroll_finished=True).filter(organization__icontains=values).count()
            orga_dict[values] = temp

        return orga_dict

    def get_labels(self):

        return ['Cantidad de estudiantes por organización']

    def get_datasets(self):
        self.index = 0
        dataset = []

        students = self.get_students()
        keys_list = list(students.keys())
        for stud, val in students.items():
            dataset.append(
                {'label': stud,
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

