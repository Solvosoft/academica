from django.db import models
from django.utils.translation import gettext_lazy as _

from .currency import CURRENCY_CHOICES

DECIMAL_PLACES = 2
DEFAULT_CURRENCY = 'USD'


class SystemCurrency(models.Model):
    currency = models.CharField(max_length=4, unique=True,
                                choices=CURRENCY_CHOICES,
                                verbose_name=_("Currency"))
    rates = models.DecimalField(
        max_digits=10,
        decimal_places=DECIMAL_PLACES,
        default=1, verbose_name=_("Change type"),
        help_text=_("1 USD is equal to X in local currency"))

    def __str__(self):
        return self.currency

    class Meta:
        ordering = ('currency',)
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")
        permissions = [
            ("can_show_dashboard", _("Can show dashboard")),
        ]


def get_default_currency():
    """Moneda por defecto de las facturas (USD), creada si no existe."""
    currency, _created = SystemCurrency.objects.get_or_create(currency=DEFAULT_CURRENCY)
    return currency.pk


class Country(models.Model):
    # Código ISO 3166-1 alfa-2 en mayúscula; la bandera se dibuja con {% flag %} (gtflags)
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    code = models.CharField(max_length=5, unique=True, verbose_name=_("Code"))

    def __str__(self):
        return self.name

    @property
    def flag(self):
        from djgentelella.flags import flag_url
        return flag_url(self.code.lower())

    class Meta:
        ordering = ('name',)
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
