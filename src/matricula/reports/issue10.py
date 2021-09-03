from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse


@permission_required('matricula.view_reports')
def consolidado_estadisticas_cursos(request):
    context = {
         'graph_url': reverse('consolidadoestcurso-list')
    }
    return render(request, 'reports/consolidado_estadisticas_cursos.html', context=context)