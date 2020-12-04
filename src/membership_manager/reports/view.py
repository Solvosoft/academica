from base64 import b64decode

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from membership_core.models import ServiceType
from membership_manager.forms import ReportForm, CreateReportTypeForm
from membership_manager.models import Report, ReportType
from membership_manager.reports.registro import REPORTES_DISPONIBLES, REPORTES_TITULOS
from membership_manager.utils import add_logentry


@permission_required('membership_manager.add_report')
def reports(request):
    context = {
        'report_type': ''
    }
    mostrar_boton = False

    if request.method == 'POST':
        is_saved = request.POST.get('is_saved', '0')
        user = request.user

        form = ReportForm(request.POST, user=user, is_saved=is_saved, initial={'grafic': 'bar'})

        if form.is_valid():

            key = form.cleaned_data['report_type']
            context['report_type']=REPORTES_TITULOS[key]

            if key in REPORTES_DISPONIBLES:

                grafico = REPORTES_DISPONIBLES[key](request, form)
                class_form_filter = grafico.get_extra_forms()

                if class_form_filter != "":
                    form_extra = class_form_filter(request.POST)

                    if form_extra.is_valid():

                        if form.do_save:
                            info_filtros = []
                            report = form.save()
                            midata = dict([(x, list(y.values_list(flat=True)) if not isinstance(y, list) else list(map(lambda x: int(x), y))) for x, y in form_extra.cleaned_data.items()])

                            info = "currency"

                            for x, y in form_extra.cleaned_data.items():
                                if y:
                                    if not isinstance(y, list):

                                        if isinstance(y.first(), ServiceType):

                                            info = "name"

                                        info_filtros.append((form_extra.fields[x].label, list(y.values_list(info, flat=True))))
                                    else:
                                        info_filtros.append((form_extra.fields[x].label, y))

                            report.extra_form = midata
                            if y:
                                report.info_filters = dict(info_filtros)
                            report.user = user
                            report.save()
                            add_logentry("membership_manager", "report", report.pk, str(report), request.user, 1)
                            messages.success(request, "Reporte guardado satisfactoriamente")
                            return redirect('reports')

                        grafico.form_filter = form_extra

                        context['form_extra'] = form_extra
                        context['tiene_filtros'] = 1
                        context['tiene_resultados'] = True
                        context['reporte_tabla'] = grafico.view_render_table()
                        context['reporte_grafico'] = grafico.view_render_graphics()
                        mostrar_boton = grafico.mostrar_descarga_grafico

                else:
                    if form.do_save:
                        report = form.save()
                        add_logentry("membership_manager", "report", report.pk, str(report), request.user, 1)
                        report.user = user
                        report.save()
                        messages.success(request, "Reporte guardado satisfactoriamente")
                        return redirect('reports')

                    context['form_extra'] = ""
                    context['tiene_filtros'] = 0
                    context['tiene_resultados'] = True
                    context['reporte_tabla'] = grafico.view_render_table()
                    context['reporte_grafico'] = grafico.view_render_graphics()
                    mostrar_boton = grafico.mostrar_descarga_grafico

        else:
            messages.warning(request, "Reporte no guardado, por favor corrija los errores")
    else:
        form = ReportForm(user=request.user, initial={'grafic': 'bar', 'is_saved': 0})

    context['form'] = form
    context['boton_descarga_grafico'] = mostrar_boton
    return render(request, 'reports.html', context=context)


@permission_required('membership_manager.view_report')
def show_report(request, pk):
    report = get_object_or_404(Report, pk=pk)
    context={'tiene_resultados': True, 'report': report}
    clear_cache = request.GET.get('nocache', 'n')
    mostrar_boton = False

    if clear_cache == 's' or report.cache_table is None or report.cache_grafic is None:
        data = {
            'country': report.country.all(),
            'start_date': report.start_date,
            'end_date' : report.end_date,
            'report_type': report.report_type,
            'grafic':   report.grafic,
            'user': report.user,
            'data_type': report.data_type
        }
        form = ReportForm(data, user=request.user,  initial={'grafic': report.grafic, 'is_saved': 0})
        form.is_valid()

        grafico = REPORTES_DISPONIBLES[report.report_type](request, form)
        class_form_filter = grafico.get_extra_forms()

        if class_form_filter:
            form_extra = class_form_filter(report.extra_form)

            if form_extra.is_valid():
                grafico.form_filter = form_extra

        report.cache_table = grafico.view_render_table()
        report.cache_grafic = grafico.view_render_graphics()
        report.save()
        add_logentry("membership_manager", "report", report.pk, str(report), request.user, 2)

    if "chart-container" in report.cache_grafic:
        mostrar_boton = True

    context['info'] = report.info_filters
    context['reporte_tabla'] = report.cache_table
    context['reporte_grafico'] = report.cache_grafic
    context['boton_descarga_grafico'] = mostrar_boton
    context['tipo_reporte'] = REPORTES_TITULOS[report.report_type]


    return render(request, 'reports/details.html', context=context)


@permission_required('membership_manager.view_report')
def list_report(request):

    context = {
        'object_list': ReportType.objects.all()
    }

    return render(request, 'reports/list.html', context=context)


def filters_extra(request, key):

    if key in REPORTES_DISPONIBLES:

        reporte = REPORTES_DISPONIBLES[key](request, None)
        form_filters = reporte.get_extra_forms()

        if form_filters == "":
            return JsonResponse({'filters': False})
        else:
            form = form_filters()
            data = {'filters': True,
                    'message': str(form.as_inline()),
                    'script': """$('select[name="eje_x"]').select2({templateResult: decore_select2, width: '100%%'});
                     $('select[name="eje_y"]').select2({templateResult: decore_select2, width: '100%%'});
                     $('select[name="eje_z"]').select2({templateResult: decore_select2, width: '100%%'});"""
            }

    return JsonResponse(data)


def download_graph(request):
    response =  HttpResponse(content_type="image/png")
    response['Content-Disposition'] = 'attachment; filename="graph.png"'
    response.write(b64decode(request.POST['imgdata']))
    return response

@permission_required('membership_manager.add_reporttype')
def add_reporttype_view(request):
    if request.method == 'POST':
        form =CreateReportTypeForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return JsonResponse({'ok': True, 'id': instance.pk, 'text': str(instance)})

        return JsonResponse({'ok': False,
                             'title': "Existe un error en el formulario",
                             'message':  render_to_string('catalogo_add.html',
                                    context={
                                        'form': form
                                    })})


    form = CreateReportTypeForm()
    data = {
        'ok':  True,
        'title': 'Ingresando información',
        'message': render_to_string('catalogo_add.html',
                                    context={
                                        'form': form
                                    })
    }

    return JsonResponse(data)