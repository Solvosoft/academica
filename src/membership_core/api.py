from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from djgentelella.objectmanagement import AuthAllPermBaseObjectManagement

from membership_core import serializers
from membership_core.models import Country, SystemCurrency


class CountryManagement(AuthAllPermBaseObjectManagement):
    """Catálogo de países (requiere los permisos del modelo según la acción)."""
    serializer_class = {
        'list': serializers.CountryDataTableSerializer,
        'create': serializers.CountrySerializer,
        'update': serializers.CountrySerializer,
        'retrieve': serializers.CountrySerializer,
        'get_values_for_update': serializers.CountrySerializer,
    }
    perms = {
        'list': ['membership_core.view_country'],
        'retrieve': ['membership_core.view_country'],
        'get_values_for_update': ['membership_core.change_country'],
        'create': ['membership_core.add_country'],
        'update': ['membership_core.change_country'],
        'partial_update': ['membership_core.change_country'],
        'destroy': ['membership_core.delete_country'],
        'detail_template': ['membership_core.view_country'],
    }
    authentication_classes = (SessionAuthentication,)
    queryset = Country.objects.all()
    search_fields = ['name', 'code']
    filterset_class = serializers.CountryFilterSet
    ordering_fields = ['name', 'code']
    ordering = ('name',)

    @action(detail=False, methods=['get'])
    def detail_template(self, request, *args, **kwargs):
        return Response({
            'title': '<% it.name %>',
            'template': '<img src="<% it.flag %>" width="32"> <% it.code %>',
        })


class SystemCurrencyManagement(AuthAllPermBaseObjectManagement):
    """Catálogo de monedas y tipo de cambio respecto al dólar."""
    serializer_class = {
        'list': serializers.SystemCurrencyDataTableSerializer,
        'create': serializers.SystemCurrencySerializer,
        'update': serializers.SystemCurrencySerializer,
        'retrieve': serializers.SystemCurrencySerializer,
        'get_values_for_update': serializers.SystemCurrencySerializer,
    }
    perms = {
        'list': ['membership_core.view_systemcurrency'],
        'retrieve': ['membership_core.view_systemcurrency'],
        'get_values_for_update': ['membership_core.change_systemcurrency'],
        'create': ['membership_core.add_systemcurrency'],
        'update': ['membership_core.change_systemcurrency'],
        'partial_update': ['membership_core.change_systemcurrency'],
        'destroy': ['membership_core.delete_systemcurrency'],
        'detail_template': ['membership_core.view_systemcurrency'],
    }
    authentication_classes = (SessionAuthentication,)
    queryset = SystemCurrency.objects.all()
    search_fields = ['currency']
    filterset_class = serializers.SystemCurrencyFilterSet
    ordering_fields = ['currency', 'rates']
    ordering = ('currency',)

    @action(detail=False, methods=['get'])
    def detail_template(self, request, *args, **kwargs):
        return Response({
            'title': '<% it.currency %> - <% it.currency_display %>',
            'template': '1 USD = <% it.rates %> <% it.currency %>',
        })
