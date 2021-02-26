from django.db import models
from .currency import CURRENCY_CHOICES
DECIMAL_PLACES=2


class SystemCurrency(models.Model):
    currency = models.CharField(max_length=4,
                                choices=CURRENCY_CHOICES,
                                verbose_name="Moneda")
    rates = models.DecimalField(
        max_digits=10,
        decimal_places=DECIMAL_PLACES,
        default=1, verbose_name="Tipo de cambio",
                              help_text="1 USD equivale a X en moneda local")

    def __str__(self):
        return self.currency

    class Meta:
        verbose_name = "Moneda"
        verbose_name_plural = "Monedas"


class Country(models.Model):
    name = models.CharField(max_length=150)
    flag = models.CharField(max_length=25)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.name
