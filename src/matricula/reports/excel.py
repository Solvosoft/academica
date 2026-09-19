from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from matricula.forms import CourseWithCoursefilterGraphForm
from matricula.models import Enroll, Period
from matricula.reports.xlsx import xlsx_response, tagify_to_text


@permission_required('matricula.view_reports')
def export_student_status_xls(request, period, status='approved'):
    file_name='students_%d_%s'%(period, status)
    filters = {
        'uncompleted': {
            'enroll_finished': True,
            'go_to_one_class': True,
            'course_status': "uncompleted",
            'group__period': period
        },
        'approved': {
            'enroll_finished': True,
            'go_to_one_class': True,
            'course_status': "approved",
            'group__period': period
        },
        'reproved': {
            'enroll_finished': True,
            'go_to_one_class': True,
            'course_status': "reproved",
            'group__period': period
        },
        'never_attend': {
            'enroll_finished': True,
            'go_to_one_class': False,
            'group__period': period
        }

    }

    if status not in filters:
        raise Http404()

    queryset = Enroll.objects.filter(**filters[status])

    form = CourseWithCoursefilterGraphForm(request.GET)
    form.mapitem = {
        'period': 'group__period__finish_date__year__in',
        'workload': 'group__course__workload__in',
        'course': 'group__course__in',
    }
    is_valid = form.is_valid()
    if is_valid:
        queryset = form.filter_queryset(queryset)

    if queryset.count() == 0:
        messages.error(request, "No hay registros para exportar")
        return redirect(reverse('list_reports'))
    column_names = [
        'group__name', 'student__user__username','student__user__email',
        'student__user__first_name', 'student__user__last_name','student__organization',
    'enroll_date', 'course_status' ]

    sheet_header  = ['Grupo', "Nombre de usuario", "Correo", "Nombre", "Apellidos", "Organización",
                     "Fecha matricula", "Estado" ]

    status_labels = {key: str(label) for key, label in Enroll.COURSE_STATUS}
    return xlsx_response(queryset, column_names, sheet_header, file_name, converters={
        5: tagify_to_text,
        7: lambda value: status_labels.get(value, value),
    })
