from django.db import models
from djmoney.settings import CURRENCY_CHOICES
from djmoney.money import Money
from djmoney.settings import DECIMAL_PLACES
from decimal import Decimal

from membership_core.currencyutils import get_currency


class SystemCurrency(models.Model):
    currency = models.CharField(max_length=4,
                                choices=CURRENCY_CHOICES,
                                verbose_name="Moneda")
    rates = models.DecimalField(
        max_digits=10,
        decimal_places=DECIMAL_PLACES,
        default=1, verbose_name="Tipo de cambio",
                              help_text="1 USD equivale a X en moneda local")


    def convert_usd_money(self, value):
        value = Decimal(value)
        return Money(value/self.rates, 'USD')

    def convert_local_money(self, value):
        value=Decimal(value)
        return Money(value*self.rates, self.currency)

    def convert_money(self, value, othercorrency):

        if othercorrency == 'USD':
            return self.convert_usd_money(value)
        if othercorrency == self.currency:
            return Money(value, self.currency)
        usd = self.convert_usd_money(value)
        newcurrency = get_currency(othercorrency, self.__class__)
        return newcurrency.convert_local_money(usd.amount)
    def __str__(self):
        return self.currency

    class Meta:
        verbose_name = "Moneda"
        verbose_name_plural = "Monedas"

class RenewalPeriod(models.Model):
    months = models.FloatField(verbose_name="meses")

    def __str__(self):
        month_name = "meses"
        month = self.months
        if month < 1:
            month = self.months*100
            month_name= "días"
        return "Cada %0.f %s"%(month, month_name)

    class Meta:
        verbose_name = "Periodo de renovación"
        verbose_name_plural = "Periodos de renovación"

class Service(models.Model):
    name = models.CharField(max_length=300, verbose_name="nombre")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

class MembershipTemplate(models.Model):
    STATES = (
        ("active", "Activa"),
        ("inactive", "Inactiva"),
        ("graceperiod", "Periodo de gracia"),
    )
    name = models.CharField(max_length=300, verbose_name="Nombre")
    annual_cost = models.FloatField(verbose_name="Costo")
    currency = models.ForeignKey(SystemCurrency, on_delete=models.CASCADE,
                                 verbose_name="Moneda")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    services = models.ManyToManyField(Service, verbose_name="Servicios")
    renewal_period = models.ForeignKey(RenewalPeriod, on_delete=models.CASCADE,
                                       verbose_name="Periodo de renovación")
    state = models.CharField(max_length=10, choices=STATES, default="active",
                             verbose_name="Estado")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Plantilla de membresías"
        verbose_name_plural = "Plantillas de membresías"