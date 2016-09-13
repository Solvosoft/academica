# encoding: utf-8

from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

# Create your models here.


@python_2_unicode_compatible
class Colon_Exchange(models.Model):
    is_dolar = models.DecimalField(max_digits=10, decimal_places=4, verbose_name=_("Amount"))

    def __str__(self):
        return "%.4f" % self.is_dolar
    
@python_2_unicode_compatible
class Bill(models.Model):
    short_description = models.CharField(max_length=300, verbose_name=_("Short description"))
    description = models.TextField(verbose_name=_("Description"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    student = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Student"))
    currency = models.CharField(max_length=3, verbose_name=_("Currency"), default="CRC")
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.TextField(max_length=300, null=True, blank=True)
 
    def __str__(self):
        return self.short_description

    class Meta:
        verbose_name = _("Bill")
        verbose_name_plural = _("Bills")
