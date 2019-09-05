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

    email = models.EmailField() # Correo electrónico
    cellphone = models.CharField(max_length=200) # celular
    phone = models.CharField(max_length=200) # Teléfono
    address = models.TextField() #Dirección
    country = CountryField() # País
    city = models.CharField(max_length=200) # Ciudad
    province = models.CharField(max_length=200) # Estado / Provincia
    postal_code = models.CharField(max_length=10) # Código Postal
    active = models.BooleanField(default=True) # Estado(Activo, Inactivo)
    currency = models.ForeignKey(SystemCurrency, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=250, choices=PAYMENT)

    class Meta:
        abstract = True

class Contact(GeneralContactInfo):
    first_name = models.CharField(max_length=250) #Nombres
    last_name = models.CharField(max_length=250) #Apellidos


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Organization(GeneralContactInfo):
    name = models.CharField(max_length=300)  #Nombre de la Organización
    initials = models.CharField(max_length=50) #SIGLA
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


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
            ("Honoraria", "Honoraria") )
    creation_date = models.DateTimeField(auto_now_add=True)
    membership_type = models.CharField(max_length=50, choices=TYPES)
    contact = models.ForeignKey(Contact, null=True, blank=True, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    annual_cost = models.FloatField()
    currency = models.ForeignKey(SystemCurrency, on_delete=models.CASCADE)
    description = models.TextField(null=True, blank=True)
    services = models.ManyToManyField(Service)
    renewal_period = models.ForeignKey(RenewalPeriod, on_delete=models.CASCADE)
    state = models.CharField(max_length=10, choices=STATES, default="active")

    def __str__(self):
        return self.name

class MembershipRenew(models.Model):
    creation_date = models.DateTimeField(auto_created=True)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    start_date = models.DateTimeField
    end_date = models.DateTimeField()
    models.ForeignKey(Membership, on_delete=models.CASCADE)
    graceperiod = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    def __str__(self):
        return "From %s to %s"%(self.start_date.strftime("%d/%m/%Y"),
                                self.end_date.strftime("%d/%m/%Y"))

class Invoice(models.Model):
    STATUS = (
        ('pending', "Pendiente"),
        ("paid", "Pagada"),
        ("inactive", "Inactiva")
    )
    creation_date = models.DateTimeField(auto_created=True)
    expiration_date = models.DateTimeField()
    payment_date = models.DateField(null=True, blank=True)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE)
    renewal_period = models.ForeignKey(MembershipRenew, on_delete=models.CASCADE)
    description = models.TextField()
    amount = models.FloatField()
    currency = models.ForeignKey(SystemCurrency, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS)
    pdf_invoice = models.FileField(upload_to="invoices/", null=True, blank=True)

    def __str__(self):
        return "%s %s %s"%(
            self.membership, self.renewal_period,
            self.get_status_display()
        )
