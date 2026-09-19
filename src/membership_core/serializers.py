from django_filters import FilterSet
from rest_framework import serializers

from membership_core.models import Country, SystemCurrency


class DataTableSerializer(serializers.Serializer):
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)


class CountrySerializer(serializers.ModelSerializer):
    flag = serializers.CharField(read_only=True)

    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'flag']


class CountryDataTableSerializer(DataTableSerializer):
    data = serializers.ListField(child=CountrySerializer(), required=True)


class CountryFilterSet(FilterSet):
    class Meta:
        model = Country
        fields = {'name': ['icontains'], 'code': ['icontains']}


class SystemCurrencySerializer(serializers.ModelSerializer):
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)

    class Meta:
        model = SystemCurrency
        fields = ['id', 'currency', 'currency_display', 'rates']


class SystemCurrencyDataTableSerializer(DataTableSerializer):
    data = serializers.ListField(child=SystemCurrencySerializer(), required=True)


class SystemCurrencyFilterSet(FilterSet):
    class Meta:
        model = SystemCurrency
        fields = {'currency': ['icontains'], 'rates': ['exact']}
