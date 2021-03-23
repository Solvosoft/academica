# encoding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from matricula.models import Student
from membership_core.models import SystemCurrency


class Bill(models.Model):
    short_description = models.CharField(
        max_length=300, verbose_name=_("Short description"))
    description = models.TextField(verbose_name=_("Description"))
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    student = models.ForeignKey(
        Student, verbose_name=_("Student"), on_delete=models.CASCADE)
    currency = models.ForeignKey(
        SystemCurrency, verbose_name=_("Currency"), default=4,
        on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.TextField(max_length=300, null=True, blank=True)
    # FIXME This relation has to be changed to OneToOneField
    enrollment = models.ForeignKey("matricula.Enroll", null=True, on_delete=models.CASCADE, verbose_name=("Enrollment"))

    def __str__(self):
        return self.short_description

    class Meta:
        verbose_name = _("Bill")
        verbose_name_plural = _("Bills")
        ordering = ['is_paid', 'student']
