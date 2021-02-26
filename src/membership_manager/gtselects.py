from django.db.models import Q
from djgentelella.groute import register_lookups
from djgentelella.views.select2autocomplete import BaseSelect2View
from membership_core.models import Country, SystemCurrency


@register_lookups(prefix="country", basename="countrybasename")
class CountryGModelLookup(BaseSelect2View):
    model = Country
    fields = ['name']


@register_lookups(prefix="currency", basename="currencybasename")
class CurrencyGModelLookup(BaseSelect2View):
    model = SystemCurrency
    fields = ['currency']
