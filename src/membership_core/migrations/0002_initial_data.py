from django.db import migrations

from membership_core.utils import country_data

# Monedas iniciales. El tipo de cambio (1 USD = X) se ajusta desde el catálogo.
INITIAL_CURRENCIES = ['USD', 'CRC']


def load_initial_data(apps, schema_editor):
    Country = apps.get_model('membership_core', 'Country')
    SystemCurrency = apps.get_model('membership_core', 'SystemCurrency')
    for code in INITIAL_CURRENCIES:
        SystemCurrency.objects.get_or_create(currency=code)
    existing = set(Country.objects.values_list('code', flat=True))
    Country.objects.bulk_create([
        Country(code=code, name=name)
        for code, name in country_data.items() if code not in existing
    ])


class Migration(migrations.Migration):

    dependencies = [
        ('membership_core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_initial_data, migrations.RunPython.noop),
    ]
