from django.db.models import Count, Q

from membership_manager.models import Membership
from membership_manager.reports.chart_builder import ChartBuilder


countries = None

class InterfazReportes():

    def __init__(self, request, form):
        self.form = form
        self.request = request
        self.filtros = {}
        self.chart = ChartBuilder()
        self.user = request.user
        self.form_filter = None
        self.girar_datos = False
        self.total = 0
        self.numero_representante = 1
        self.lista_elementos_grafico = []
        self.lista_registros = []
        self.mostrar_descarga_grafico = True

        global countries

        self.data = {
            'labels': [],
            'datasets': ["",
                         {'dataset': [], 'dataset_labels': []}],
            'axis_titles': []
        }

        if form is not None:

            countries = self.form.cleaned_data['country']
            self.tipo_grafico = self.form.cleaned_data['grafic'] or 'bar'
            self.tipo_dato = self.form.cleaned_data['data_type'] or 'numerical'

            if self.form.cleaned_data['start_date']:
                self.filtros['creation_date__gte'] = self.form.cleaned_data['start_date']

            if self.form.cleaned_data['end_date']:
                self.filtros['creation_date__lte'] = self.form.cleaned_data['end_date']

        else:
            self.paises = None
            self.tipo_grafico = 'bar'
            self.tipo_dato = 'numerical'

        self.filtros['state'] = "active"

    def view_render_table(self):
        return ""

    def view_render_graphics(self):
        return ""

    def get_extra_forms(self):
        return ""

    def get_horizontal_total(self, titles_list, record_list, starting_column):
        titles_list.append("Total")
        for x, element in enumerate(record_list):
            record_list[x].append(sum(record_list[x][starting_column:]))

    def get_vertical_total(self, titles_list, record_list, starting_column, add_horizontally):

        if starting_column ==1:
            record_list.append(["Total"] + [0] * (len(titles_list)-1))
        else:
            record_list.append(["Total", "-----"] + [0] * (len(titles_list)-2))

        for x, element in enumerate(record_list):

            if x==len(record_list)-1:
                if add_horizontally:
                    record_list[-1][-1] += sum(record_list[x][starting_column:-1])
                break

            for y in range(starting_column, len(element)):
                record_list[-1][y] += record_list[x][y]

    def get_totals(self, titles_list, record_list, starting_column, add_horizontally, add_vertically):

        if add_horizontally:
            self.get_horizontal_total(titles_list, record_list, starting_column)

        if add_vertically:
            self.get_vertical_total(titles_list, record_list, starting_column, add_horizontally)

    def get_percentages(self, record_list, total, starting_column):

        for x, element in enumerate(record_list):

            if x == len(record_list)-1:
                if starting_column != 1:
                    starting_column = 2

            for y in range(starting_column, len(element)):
                record_list[x][y] = str(round(record_list[x][y] * 100 / total, 4) if total > 0 else 0.0) + "%"


class BaseDataBuilder:
    def __init__(self):
        self._cached = False

    def get_x_axis(self):
        return None

    def get_y_axis(self):
        return None

    def get_z_axis(self):
        return None

    def filter_axis(self, x_value, y_value, z_value=None):
        return {}

    def get_base_query(self):
        queryset = Membership.objects.filter(**self.filtros)
        if countries:
            queryset = queryset.filter(Q(organization__country__in=countries)|Q(
                contact__country__in=countries))

        return queryset

    def get_x_title(self, value):
        return str(value)

    def get_y_title(self, value):
        return str(value)

    def get_z_title(self, value):
        return str(value)

    def get_x_label(self, value):
        return str(value)

    def get_y_label(self, value):
        return str(value)

    def get_z_label(self, value):
        return str(value)

    def get_intersection_name(self):
        return ""
    def get_second_intersection_name(self):
        return ""

    def get_extra_filters(self):
        return None


class CatalogxCatalogMinix(BaseDataBuilder):

    def get_data(self):
        if self._cached:
            return
        self.titulo = [self.get_intersection_name()]
        x_data, y_data = self.get_x_axis(), self.get_y_axis()
        self.get_extra_filters()
        querysetbase = self.get_base_query()
        self.total = querysetbase.count()
        items = {}
        list_items = []
        count = 0
        for x in x_data:
            for y in y_data:
                key = "k_%s_%s" % (x.pk, y.pk)
                items[key] = Count('id', filter=self.filter_axis(x.pk, y.pk))
                count += 1
                if count == 1500:
                    list_items.append(items)
                    items = {}
                    count=0
        if items:
            list_items.append(items)
        result = {}
        for item in list_items:
            resultq = querysetbase.aggregate(**item)
            result.update(resultq)

        result = querysetbase.aggregate(**items)
        x_size = y_data.count()
        self.tabla_registros = [[self.get_y_label(obj)] + [0] * x_size for obj in x_data]
        for x, xdata in enumerate(x_data):
            for y, ydata in enumerate(y_data):
                key = "k_%s_%s" % (xdata.pk, ydata.pk)
                self.tabla_registros[x][y + 1] = result[key]
                if not x:
                    self.titulo.append(self.get_y_title(ydata))

            registros = self.tabla_registros[x][1:]

            if self.tipo_dato == "percentaje":
                registros = [round(x * 100 / self.total, 4) if self.total > 0 else 0.0 for x in registros]

            self.data['datasets'][1]['dataset'].append(registros)
            self.data['datasets'][1]['dataset_labels'].append(self.get_x_label(xdata))
            self.data['labels'] = self.titulo[1:]
        self._cached=True