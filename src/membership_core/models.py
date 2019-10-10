from django.db import models
from djmoney.settings import CURRENCY_CHOICES


class SystemCurrency(models.Model):
    currency = models.CharField(max_length=4,
                                choices=CURRENCY_CHOICES,
                                verbose_name="moneda")

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
        verbose_name = "Plantilla de membresias"
        verbose_name_plural = "Plantillas de membresias"