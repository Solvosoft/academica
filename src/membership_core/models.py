from django.db import models
from .currency import CURRENCY_CHOICES
DECIMAL_PLACES=2
from django.utils.translation import gettext as _


class SystemCurrency(models.Model):
    currency = models.CharField(max_length=4,
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
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")
        permissions = [
            ("can_show_dashboard", _("Can show dashboard")),
        ]


class Country(models.Model):
    name = models.CharField(max_length=150)
    flag = models.CharField(max_length=25)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
