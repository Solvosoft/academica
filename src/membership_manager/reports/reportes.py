from collections import Counter

from django import forms
from django.db.models import Q
from django.template.loader import render_to_string
from djgentelella.forms.forms import CustomForm
from djgentelella.widgets import core as genwidgets

from membership_core.models import SystemCurrency, Country, ServiceType
from membership_manager.reports.base import InterfazReportes, BaseDataBuilder, countries


class Reporte_Factura_Pagada_Moneda(InterfazReportes, BaseDataBuilder):

    """
    """

    def __init__(self, request, form):
        super().__init__(request, form)
        labels = ['Monedas']
        if self.tipo_grafico == "line":
            labels = ['Facturas']
        self.data = {
            'labels': labels,
            'datasets': ['Facturas pagadas según moneda', {'dataset': [], 'dataset_labels': []}],
            'axis_titles': ['', 'Facturas']
        }
        self.titulo = ['Monedas', 'Facturas']
        self._cached = False

    def get_x_axis(self):
        queryset = SystemCurrency.objects.all()
        if self.form_filter is not None and self.form_filter.cleaned_data['eje_x']:
            queryset = queryset.filter(id__in=self.form_filter.cleaned_data['eje_x'])
        return queryset

    def get_extra_forms(self):
        class extra_form(CustomForm, forms.Form):
            eje_x = forms.ModelMultipleChoiceField(queryset=SystemCurrency.objects.all(),
                                                   widget=genwidgets.SelectMultiple, required=False, label="Moneda")
        return extra_form

    def get_extra_filters(self):
        self.filtros['mem_inv__currency__in'] = self.get_x_axis()
        self.filtros['mem_inv__status'] = "paid"

    def get_data(self):
        if self._cached:
            return

        self.get_extra_filters()
        invoices__currency = list(self.get_base_query().values_list('mem_inv__currency__currency', flat=True))
        list_currency = Counter(invoices__currency)
        self.total = len(invoices__currency)

        for currency in self.get_x_axis():

            cantidad = list_currency[currency.currency]
            self.data['datasets'][1]['dataset_labels'].append(currency.currency)
            self.lista_registros.append([currency.currency, cantidad])

            if self.tipo_dato == "percentaje":
                cantidad = round(cantidad * 100 / self.total, 4) if self.total > 0 else 0.0

            self.data['datasets'][1]['dataset'].append([cantidad])
        self._cached = True

    def view_render_table(self):
        self.get_data()

        self.get_totals(self.titulo, self.lista_registros, 1, False, True)

        if self.tipo_dato=="percentaje":
            self.get_percentages(self.lista_registros, self.total, 1)

        context = {'titulos': self.titulo,
                   'registros': self.lista_registros
                   }

        return render_to_string("tabla.html", context, request=self.request)

    def view_render_graphics(self):
        self.get_data()
        self.girar_datos = True
        context = {'json': self.chart.create_chart(self.tipo_grafico, self.data, girar_datos=self.girar_datos),
                   'graphsize': 'middle'}
        return render_to_string("grafico.html", context, request=self.request)

class Reporte_Membresia_Pais(InterfazReportes, BaseDataBuilder):

    """
    """

    def __init__(self, request, form):
        super().__init__(request, form)
        labels = ['Paises']
        if self.tipo_grafico == "line":
            labels = ['Membresías']
        self.data = {
            'labels': labels,
            'datasets': ['Membresías por país', {'dataset': [], 'dataset_labels': []}],
            'axis_titles': ['', 'Membresías']
        }
        self.titulo = ['Paises', 'Membresías']
        self._cached = False
        self.queryset = self.get_base_query()

    def get_x_axis(self):
        return countries if countries else Country.objects.all()

    def get_data(self):
        if self._cached:
            return

        self.total = self.queryset.count

        for country in self.get_x_axis():

            cantidad = self.queryset.filter(Q(organization__country=country)|Q(
                contact__country=country)).count()
            self.data['datasets'][1]['dataset_labels'].append(country)
            self.lista_registros.append([country, cantidad])

            if self.tipo_dato == "percentaje":
                cantidad = round(cantidad * 100 / self.total, 4) if self.total > 0 else 0.0

            self.data['datasets'][1]['dataset'].append([cantidad])
        self._cached = True

    def view_render_table(self):
        self.get_data()

        self.get_totals(self.titulo, self.lista_registros, 1, False, True)

        if self.tipo_dato=="percentaje":
            self.get_percentages(self.lista_registros, self.total, 1)

        context = {'titulos': self.titulo,
                   'registros': self.lista_registros
                   }

        return render_to_string("tabla.html", context, request=self.request)

    def view_render_graphics(self):
        self.get_data()
        self.girar_datos = True
        context = {'json': self.chart.create_chart(self.tipo_grafico, self.data, girar_datos=self.girar_datos),
                   'graphsize': 'middle'}
        return render_to_string("grafico.html", context, request=self.request)


class Reporte_Membresia_Moneda(InterfazReportes, BaseDataBuilder):

    """
    """

    def __init__(self, request, form):
        super().__init__(request, form)
        labels = ['Monedas']
        if self.tipo_grafico == "line":
            labels = ['Membresías']
        self.data = {
            'labels': labels,
            'datasets': ['Membresías según moneda', {'dataset': [], 'dataset_labels': []}],
            'axis_titles': ['', 'Membresías']
        }
        self.titulo = ['Monedas', 'Membresías']
        self._cached = False
        self.queryset = self.get_base_query()

    def get_x_axis(self):
        queryset = SystemCurrency.objects.all()
        if self.form_filter is not None and self.form_filter.cleaned_data['eje_x']:
            queryset = queryset.filter(id__in=self.form_filter.cleaned_data['eje_x'])
        return queryset

    def get_extra_forms(self):
        class extra_form(CustomForm, forms.Form):
            eje_x = forms.ModelMultipleChoiceField(queryset=SystemCurrency.objects.all(),
                                                   widget=genwidgets.SelectMultiple, required=False, label="Moneda")

        return extra_form

    def get_extra_filters(self):
        self.filtros['currency__in'] = self.get_x_axis()

    def get_data(self):
        if self._cached:
            return

        self.get_extra_filters()
        self.total = self.queryset.count()

        for currency in self.get_x_axis():

            cantidad = self.queryset.filter(currency=currency).count()
            self.data['datasets'][1]['dataset_labels'].append(currency.currency)
            self.lista_registros.append([currency.currency, cantidad])

            if self.tipo_dato == "percentaje":
                cantidad = round(cantidad * 100 / self.total, 4) if self.total > 0 else 0.0

            self.data['datasets'][1]['dataset'].append([cantidad])
        self._cached = True

    def view_render_table(self):
        self.get_data()

        self.get_totals(self.titulo, self.lista_registros, 1, False, True)

        if self.tipo_dato=="percentaje":
            self.get_percentages(self.lista_registros, self.total, 1)

        context = {'titulos': self.titulo,
                   'registros': self.lista_registros
                   }

        return render_to_string("tabla.html", context, request=self.request)

    def view_render_graphics(self):
        self.get_data()
        self.girar_datos = True
        context = {'json': self.chart.create_chart(self.tipo_grafico, self.data, girar_datos=self.girar_datos),
                   'graphsize': 'middle'}
        return render_to_string("grafico.html", context, request=self.request)


class Reporte_Membresia_Servicios(InterfazReportes, BaseDataBuilder):

    """
    """

    def __init__(self, request, form):
        super().__init__(request, form)
        labels = ['Servicios']
        if self.tipo_grafico == "line":
            labels = ['Membresías']
        self.data = {
            'labels': labels,
            'datasets': ['Membresías según servicio', {'dataset': [], 'dataset_labels': []}],
            'axis_titles': ['', 'Membresías']
        }
        self.titulo = ['Servicios', 'Membresías']
        self._cached = False
        self.queryset = self.get_base_query()

    def get_x_axis(self):
        queryset = ServiceType.objects.all()
        if self.form_filter is not None and self.form_filter.cleaned_data['eje_x']:
            queryset = queryset.filter(id__in=self.form_filter.cleaned_data['eje_x'])
        return queryset

    def get_extra_forms(self):
        class extra_form(CustomForm, forms.Form):
            eje_x = forms.ModelMultipleChoiceField(queryset=ServiceType.objects.all(),
                                                   widget=genwidgets.SelectMultiple, required=False, label="Servicio")

        return extra_form


    def get_extra_filters(self):
        self.filtros['service__servicetype__in'] = self.get_x_axis()

    def get_data(self):
        if self._cached:
            return

        self.get_extra_filters()
        self.total = self.queryset.count()

        for service in self.get_x_axis():

            cantidad = self.queryset.filter(service__servicetype=service).count()
            self.data['datasets'][1]['dataset_labels'].append(service.name)
            self.lista_registros.append([service.name, cantidad])

            if self.tipo_dato == "percentaje":
                cantidad = round(cantidad * 100 / self.total, 4) if self.total > 0 else 0.0

            self.data['datasets'][1]['dataset'].append([cantidad])
        self._cached = True

    def view_render_table(self):
        self.get_data()

        self.get_totals(self.titulo, self.lista_registros, 1, False, True)

        if self.tipo_dato=="percentaje":
            self.get_percentages(self.lista_registros, self.total, 1)

        context = {'titulos': self.titulo,
                   'registros': self.lista_registros
                   }

        return render_to_string("tabla.html", context, request=self.request)

    def view_render_graphics(self):
        self.get_data()
        self.girar_datos = True
        context = {'json': self.chart.create_chart(self.tipo_grafico, self.data, girar_datos=self.girar_datos),
                   'graphsize': 'middle'}
        return render_to_string("grafico.html", context, request=self.request)