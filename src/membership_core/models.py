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

class ServiceType(models.Model):
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
        ("graceperiod", "Período de gracia"),
    )
    name = models.CharField(max_length=300, verbose_name="Nombre")
    annual_cost = models.FloatField(verbose_name="Costo")
    currency = models.ForeignKey(SystemCurrency, on_delete=models.CASCADE,
                                 verbose_name="Moneda")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    renewal_period = models.ForeignKey(RenewalPeriod, on_delete=models.CASCADE,
                                       verbose_name="Período de renovación")
    state = models.CharField(max_length=15, choices=STATES, default="active",
                             verbose_name="Estado")
    free_membership = models.BooleanField(default=False, verbose_name="¿Membresía gratuita sin factura?")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Plantilla de membresías"
        verbose_name_plural = "Plantillas de membresías"


class ServiceMT(models.Model):
    membership = models.ForeignKey(MembershipTemplate, on_delete=models.CASCADE,
                                   verbose_name="Membresía", null=True, blank=True)
    servicetype = models.ForeignKey(ServiceType, on_delete=models.DO_NOTHING,
                                    verbose_name="Tipo de servicio")
    description = models.CharField(max_length=250, verbose_name="Descripción", default="Sin descripción")
    observations = models.CharField(max_length=500, null=True, blank=True,
                                    verbose_name="Observaciones")

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
        ordering = ('membership',)


class Country(models.Model):
    name = models.CharField(max_length=150)
    flag = models.CharField(max_length=25)
    code = models.CharField(max_length=5)

    def __str__(self):
        return self.name
