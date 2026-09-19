from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from membership_core.forms import CountryForm, SystemCurrencyForm


def _catalog_context(form_class):
    return {
        'create_form': form_class(prefix='create'),
        'update_form': form_class(prefix='update'),
    }


@permission_required('membership_core.view_country')
def catalog_country(request):
    return render(request, 'catalog/country.html', _catalog_context(CountryForm))


@permission_required('membership_core.view_systemcurrency')
def catalog_currency(request):
    return render(request, 'catalog/currency.html', _catalog_context(SystemCurrencyForm))
