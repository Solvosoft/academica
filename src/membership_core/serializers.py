from django_filters import FilterSet
from rest_framework import serializers

from membership_core.models import Country, SystemCurrency


class ActionsMixin(serializers.Serializer):
    # ObjectCRUD necesita la columna "actions"; un dict vacío habilita las acciones por defecto.
    actions = serializers.SerializerMethodField()

    def get_actions(self, obj):
        return {}


class DataTableSerializer(serializers.Serializer):
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)


class CountrySerializer(serializers.ModelSerializer):
    flag = serializers.CharField(read_only=True)

    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'flag']


class CountryTableSerializer(ActionsMixin, CountrySerializer):
    class Meta(CountrySerializer.Meta):
        fields = CountrySerializer.Meta.fields + ['actions']


class CountryDataTableSerializer(DataTableSerializer):
    data = serializers.ListField(child=CountryTableSerializer(), required=True)


class CountryFilterSet(FilterSet):
    class Meta:
        model = Country
        fields = {'name': ['icontains'], 'code': ['icontains']}


class SystemCurrencySerializer(serializers.ModelSerializer):
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)

    class Meta:
        model = SystemCurrency
        fields = ['id', 'currency', 'currency_display', 'rates']


class SystemCurrencyTableSerializer(ActionsMixin, SystemCurrencySerializer):
    class Meta(SystemCurrencySerializer.Meta):
        fields = SystemCurrencySerializer.Meta.fields + ['actions']


class SystemCurrencyDataTableSerializer(DataTableSerializer):
    data = serializers.ListField(child=SystemCurrencyTableSerializer(), required=True)


class SystemCurrencyFilterSet(FilterSet):
    class Meta:
        model = SystemCurrency
        fields = {'currency': ['icontains'], 'rates': ['exact']}
