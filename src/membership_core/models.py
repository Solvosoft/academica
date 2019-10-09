from django.db import models
from djmoney.settings import CURRENCY_CHOICES


class SystemCurrency(models.Model):
    currency = models.CharField(max_length=4, choices=CURRENCY_CHOICES)

    def __str__(self):
        return self.currency


class RenewalPeriod(models.Model):
    months = models.FloatField()

    def __str__(self):
        month_name = "months"
        month = self.months
        if month < 1:
            month = self.months*100
            month_name= "days"
        return "Every %0.f %s"%(month, month_name)


class Service(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class MembershipTemplate(models.Model):
    STATES = (
        ("active", "Activa"),
        ("inactive", "Inactiva"),
        ("graceperiod", "Periodo de gracia"),
    )
    name = models.CharField(max_length=300)
    annual_cost = models.FloatField()
    currency = models.ForeignKey(SystemCurrency, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    services = models.ManyToManyField(Service)
    renewal_period = models.ForeignKey(RenewalPeriod, on_delete=models.CASCADE)
    state = models.CharField(max_length=10, choices=STATES, default="active")

    def __str__(self):
        return self.name