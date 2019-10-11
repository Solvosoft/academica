from django.db import models
from django_countries.fields import CountryField

from membership_core.models import SystemCurrency, RenewalPeriod, Service


class GeneralContactInfo(models.Model):
    PAYMENT = (
        ("Chash", "Efectivo"),
        ("Bank transfer", "Transferencia bancaria"),
        ("Paypal", "Paypal"),
        ("Bitcoins", "Bitcoins")
    )

    email = models.EmailField(verbose_name="Correo electrónico")  # Correo electrónico
    cellphone = models.CharField(max_length=200, verbose_name="celular")  # celular
    phone = models.CharField(max_length=200, verbose_name="Teléfono")  # Teléfono
    address = models.TextField(verbose_name="Dirección")  # Dirección
    country = CountryField(verbose_name="País")  # País
    city = models.CharField(max_length=200, verbose_name="Ciudad")  # Ciudad
    province = models.CharField(max_length=200, verbose_name="Provincia")  # Estado / Provincia
    postal_code = models.CharField(max_length=10, verbose_name="Código postal")  # Código Postal
    active = models.BooleanField(default=True, verbose_name="Activo")  # Estado(Activo, Inactivo)
    currency = models.ForeignKey(SystemCurrency, on_delete=models.CASCADE,
                                 verbose_name="Moneda")
    payment_method = models.CharField(max_length=250, choices=PAYMENT,
                                      verbose_name="Método de pago")

    class Meta:
        abstract = True


class Contact(GeneralContactInfo):
    first_name = models.CharField(max_length=250, verbose_name="Nombres")  # Nombres
    last_name = models.CharField(max_length=250, verbose_name="Apellidos")  # Apellidos

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    class Meta:
        verbose_name = "Contacto"
        verbose_name_plural = "Contactos"

class Organization(GeneralContactInfo):
    name = models.CharField(max_length=300, verbose_name="Nombre")  # Nombre de la Organización
    initials = models.CharField(max_length=50, verbose_name="Sigla")  # SIGLA
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, verbose_name="Contacto")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"


class Membership(models.Model):
    STATES = (
        ("active", "Activa"),
        ("inactive", "Inactiva"),
        ("graceperiod", "Periodo de gracia"),
    )
    TYPES = (("Personal", "Personal"),
             ("Radial", "Radial"),
             ("Organizacional", "Organizacional"),
             ("Global", "Global"),
             ("Honoraria", "Honoraria"))
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    membership_type = models.CharField(max_length=50, choices=TYPES, verbose_name="Tipo de membresía")
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Contato")
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, verbose_name="Nombre")
    annual_cost = models.FloatField(verbose_name="Costo")
    currency = models.ForeignKey(SystemCurrency, on_delete=models.CASCADE, verbose_name="Moneda")
    description = models.TextField(null=True, blank=True, verbose_name="Descripción")
    services = models.ManyToManyField(Service, verbose_name="Servicios")
    renewal_period = models.ForeignKey(RenewalPeriod, on_delete=models.CASCADE,
                                       verbose_name="Periodo de renovación")
    state = models.CharField(max_length=10, choices=STATES, default="active",
                             verbose_name="Estado")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"

class MembershipRenew(models.Model):
    creation_date = models.DateTimeField(auto_created=True,
                                         verbose_name="Fecha de creación")
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE,
                                   verbose_name="Membresía")
    start_date = models.DateTimeField(verbose_name="Fecha de inicio")
    end_date = models.DateTimeField(verbose_name="Fecha de finalización")
    graceperiod = models.BooleanField(default=False, verbose_name="Periodo de gracia")
    active = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return "From %s to %s" % (self.start_date.strftime("%d/%m/%Y"),
                                  self.end_date.strftime("%d/%m/%Y"))

    class Meta:
        verbose_name = "Renovación de membresía"
        verbose_name_plural = "Renovaciones de membresía"

class Invoice(models.Model):
    STATUS = (
        ('pending', "Pendiente"),
        ("paid", "Pagada"),
        ("inactive", "Inactiva")
    )
    creation_date = models.DateTimeField(auto_created=True,
                                         verbose_name="Fecha de creación")
    expiration_date = models.DateTimeField(verbose_name="Fecha de expiración")
    payment_date = models.DateField(null=True, blank=True, verbose_name="Fecha de pago")
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, verbose_name="Membresía")
    renewal_period = models.ForeignKey(MembershipRenew, on_delete=models.CASCADE,
                                       verbose_name="Periodo de renovación")
    description = models.TextField(verbose_name="Descripción")
    amount = models.FloatField(verbose_name="Cantidad")
    currency = models.ForeignKey(SystemCurrency, on_delete=models.CASCADE, verbose_name="Moneda")
    status = models.CharField(max_length=10, choices=STATUS, verbose_name="Estado")
    pdf_invoice = models.FileField(upload_to="invoices/", null=True, blank=True, verbose_name="Factura en PDF")

    def __str__(self):
        return "%s %s %s" % (
            self.membership, self.renewal_period,
            self.get_status_display()
        )

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"