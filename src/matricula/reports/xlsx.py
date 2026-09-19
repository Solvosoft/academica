from datetime import datetime
from io import BytesIO

from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook

from matricula.utils import organization_names

XLSX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


def tagify_to_text(value):
    """Convierte el JSON de tagify ([{"value": "x"}, ...]) en "x, y"."""
    return ", ".join(organization_names(value))


def _cell_value(value):
    if isinstance(value, datetime) and timezone.is_aware(value):
        return timezone.localtime(value).replace(tzinfo=None)
    return value


def xlsx_response(queryset, column_names, headers, file_name, converters=None):
    """
    Exporta ``queryset.values_list(*column_names)`` a un .xlsx.

    ``converters`` es un dict {índice_de_columna: función} para transformar
    valores antes de escribirlos.
    """
    converters = converters or {}
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(headers)
    for row in queryset.values_list(*column_names):
        sheet.append([_cell_value(converters[i](value) if i in converters else value)
                      for i, value in enumerate(row)])

    output = BytesIO()
    workbook.save(output)
    response = HttpResponse(output.getvalue(), content_type=XLSX_CONTENT_TYPE)
    response['Content-Disposition'] = 'attachment; filename="%s.xlsx"' % file_name
    return response
