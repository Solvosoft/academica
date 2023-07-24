# encoding: utf-8
from django.db import models
from django.utils.safestring import mark_safe
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
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.short_description

    class Meta:
        verbose_name = _("Bill")
        verbose_name_plural = _("Bills")
        ordering = ['is_paid', 'student']


class SinpeMovilBill(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, verbose_name="Nombre del depositante",
                            help_text="Poner el nombre del dueño del teléfono desde donde se envía el sinpe")
    group_name = models.CharField(max_length=256, verbose_name="Grupo", help_text="Nombre del grupo a pagar")
    transaction_code = models.CharField(max_length=256, verbose_name="Código de trasacción",
                                        help_text="Opcional: Escriba el número de transacción que le proporciona el comprobante de SINPE")

    verified = models.BooleanField(default=False)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    description=models.TextField(
        verbose_name="Información de factura electrónica",
        help_text="Pon cualquier información que nos permita emitirte la factura, información como:  Cédula/Correo electrónico/Teléfono")

    def __str__(self):
        return """
        Sinpe Movil creado en %s con código %s en para %s
        """%(self.created_date.strftime("%Y-%m-%d %H:%M:%S"), self.transaction_code,  self.group_name

        )


class BankBill(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50, verbose_name="Nombre del depositante",
                            help_text="Nombre del dueño de la cuenta que realiza el deposito")
    group_name = models.CharField(max_length=256, verbose_name="Grupo", help_text="Nombre del grupo a pagar")
    payment_document = models.FileField(upload_to='bank')
    verified = models.BooleanField(default=False)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    description=models.TextField(
        verbose_name="Información de factura electrónica",
        help_text="Pon cualquier información que nos permita emitirte la factura, información como:  Cédula/Correo electrónico/Teléfono")

    def __str__(self):
        return mark_safe("""
        Deposito bancario creado en %s con comprobante <a href="%s" target="_blank">Ver</a> en para %s
        """%(self.created_date.strftime("%Y-%m-%d %H:%M:%S"), self.payment_document.url,  self.group_name

        ))
