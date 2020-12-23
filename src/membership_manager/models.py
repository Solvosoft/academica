import textwrap

from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField
from django.utils.safestring import mark_safe

from membership_core.models import SystemCurrency, RenewalPeriod,\
    ServiceType, Country

PAYMENT = (
    ("Cash", "Efectivo"),
    ("Bank transfer", "Transferencia bancaria"),
    ("Paypal", "Paypal"),
    ("Bitcoins", "Bitcoins"),
    ('MoneyGram', 'MoneyGram'),
    ('WesterUnion', 'WesterUnion'),
    ('Transferencia Bancaria Argentina', 'Transferencia Bancaria Argentina')
)

IDS_TYPE = (
    ('CIF', 'CIF'), ('RFC', 'RFC'),
    ('RUT', 'RUT'), ('NIT', 'NIT'), ('CUIT', 'CUIT'), ('RTN', 'RTN'),
    ('ETC', 'ETC'),
    ('cedula_juridica', 'Cédula Jurídica')
)


class GeneralContactInfo(models.Model):
    email = models.EmailField(verbose_name="Correo electrónico")  # Correo electrónico
    cellphone = models.CharField(max_length=200, verbose_name="celular", null=True, blank=True)  # celular
    phone = models.CharField(max_length=200, verbose_name="Teléfono", null=True, blank=True )  # Teléfono
    address = models.TextField(verbose_name="Dirección", null=True, blank=True )  # Dirección
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, verbose_name="País")
    city = models.CharField(max_length=200, verbose_name="Ciudad", null=True, blank=True)  # Ciudad
    province = models.CharField(max_length=200, verbose_name="Provincia", null=True, blank=True)  # Estado / Provincia
    postal_code = models.CharField(max_length=10, verbose_name="Código postal", null=True, blank=True)  # Código Postal
    active = models.BooleanField(default=True, verbose_name="Activo")  # Estado(Activo, Inactivo)
    currency = models.ForeignKey(SystemCurrency, on_delete=models.SET_DEFAULT, default=4,
                                 verbose_name="Moneda")
    payment_method = models.CharField(max_length=250, choices=PAYMENT,
                                      verbose_name="Método de pago", null=True, blank=True)

    @property
    def get_region(self):
        data = []
        if self.city:
            data.append(self.city)
        if self.province:
            data.append(self.province)
        return ", ".join(data)

    class Meta:
        abstract = True


class Organization(GeneralContactInfo):

    name = models.CharField(max_length=300, verbose_name="Nombre")  # Nombre de la Organización
    initials = models.CharField(max_length=50, verbose_name="Sigla", null=True, blank=True)  # SIGLA
    type = models.BooleanField(default=False)  # Será falso si es organizacion, true si es contacto
    contacts = models.ManyToManyField('self', blank=True, verbose_name="Contactos")
    identification_type = models.CharField(max_length=50, null=True, blank=True, choices=IDS_TYPE, verbose_name="Tipo de identificación")
    identification  = models.CharField(max_length=50, null=True, blank=True,verbose_name="Número de Identificación")

    def __str__(self):
        mstr = self.name[:80]
        if self.initials and self.initials != " ":
            mstr = mstr +' (' + self.initials +')'

        return mstr

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        ordering = ['name']


class Membership(models.Model):
    STATES = (
        ("active", "Activa"),
        ("inactive", "Inactiva"),

    )
    TYPES = (("Personal", "Personal"),
             ("Radial", "Radial"),
             ("Organizacional", "Organizacional"),
             ("Global", "Global"),
             ("Honoraria", "Honoraria"),
             ('Básica', 'Básica'),
             ('Streaming.la', 'Streaming.la')
             )
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    membership_type = models.CharField(max_length=50, choices=TYPES, verbose_name="Tipo de membresía")
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.CASCADE)
    annual_cost = models.FloatField(verbose_name="Costo")
    currency = models.ForeignKey(SystemCurrency, on_delete=models.SET_DEFAULT, default=4, verbose_name="Moneda")
    renewal_period = models.ForeignKey(RenewalPeriod, on_delete=models.CASCADE,
                                       verbose_name="Período de renovación")
    state = models.CharField(max_length=11, choices=STATES, default="active",
                             verbose_name="Estado")
    apply_fees = models.BooleanField(default=False, verbose_name="Aplicar impuestos", help_text="Si no se selecciona, el campo de impuestos es ignorado")
    fees = models.DecimalField(default="13.00", null=True, blank=True, verbose_name="Impuestos",
                               help_text="Un número de 0 a 100", max_digits=6, decimal_places=2)

    last_renew_start_date = models.DateField(null=True, blank=True)
    free_membership = models.BooleanField(default=False, verbose_name="¿Membresía gratuita sin factura?")

    @property
    def name(self):
        if self.organization and self.organization.name:
            return self.organization.name
        return "Membresia sin nombre"

    @property
    def last_renew(self):
        renew = self.renews.filter(encobro=True, active=True).order_by(
            'end_date', 'pk').last()
        if renew:
            return renew.start_date

    @property
    def country(self):
        country = None
        if self.organization:
            country = self.organization.country
        return country

    @property
    def email(self):
        email = None
        if self.organization:
            email = self.organization.email
        return email

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
        ordering = ('state', 'organization', )
        permissions = [
            ("can_show_dashboard", "Can show dashboard"),
        ]


class Service(models.Model):
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE,
                                   verbose_name="Membresía")
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
        ordering = ('membership', )

class MembershipRenew(models.Model):
    creation_date = models.DateTimeField(auto_created=True,
                                         verbose_name="Fecha de creación")
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE,
                                   verbose_name="Membresía"
                                   , related_name='renews')
    start_date = models.DateField(verbose_name="Fecha de inicio")

    end_date = models.DateField(verbose_name="Fecha de finalización")
    encobro = models.BooleanField(default=False, verbose_name="En cobro")
    active = models.BooleanField(default=True, verbose_name="Activo")

    def __str__(self):
        return "De %s a %s" % (self.start_date.strftime("%d/%m/%Y"),
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
    creation_date = models.DateField(auto_created=True,
                                         verbose_name="Fecha de creación")
    expiration_date = models.DateField(verbose_name="Fecha de expiración")
    payment_date = models.DateField(null=True, blank=True, verbose_name="Fecha de pago")
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE,
                                   verbose_name="Membresía",related_name='mem_inv')
    renewal_period = models.ForeignKey(MembershipRenew, on_delete=models.CASCADE,
                                       verbose_name="Periodo de renovación",
                                       related_name='inv_m_renews')
    description = models.TextField(verbose_name="Descripción")
    amount = models.FloatField(verbose_name="Cantidad")
    currency = models.ForeignKey(SystemCurrency, on_delete=models.SET_DEFAULT, default=4, verbose_name="Moneda")
    status = models.CharField(max_length=10, choices=STATUS, verbose_name="Estado")
    pdf_invoice = models.FileField(upload_to="invoices/", null=True, blank=True, verbose_name="Factura en PDF")
    code = models.CharField(max_length=20, null=True, blank=True, verbose_name="Código de la Factura")

    payment_method = models.CharField(max_length=250, choices=PAYMENT,
                                      verbose_name="Método de pago", null=True, blank=True)

    transaction_number = models.CharField(max_length=250, verbose_name="Número de transaccción", null=True, blank=True)

    receipt = models.FileField(upload_to='comprobantes/', null=True, blank=True,
                                   verbose_name="Comprobante de pago")

    def __str__(self):
        return "%s %s %s" % (
            self.membership, self.renewal_period,
            self.get_status_display()
        )

    @property
    def membership_name(self):
        text = str(self.membership)
        lines=textwrap.wrap(text, 50)
        dev = "<br>".join(lines)
        return mark_safe(dev)

    @property
    def total_amount(self):
        amount = self.amount
        if self.membership.apply_fees:
            amount = amount* float(1+self.membership.fees/100)
        return "%.2f"%amount

    @property
    def fees(self):
        if not self.membership.apply_fees:
            return ''
        amount = self.amount
        amount = amount* float(self.membership.fees/100)
        return "%.2f"%(amount)

    @property
    def feed_percent(self):
        if not self.membership.apply_fees:
            return ''
        fee = self.membership.fees
        return "(%d %%)"%(fee)

    @property
    def status_color(self):
        color = 'background-color: gray;'
        if self.status == 'pending':
            color = 'background-color: red;'
        elif self.status == 'paid':
            color = 'background-color: green;'
        return color

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"


class ActivityReport(models.Model):
    ATYPES = (
        (0, 'Mantenimiento del sistema'),
        (1, 'Presencial'),
        (2, 'Fallo en servicio'),
        (3, 'Capacitación'),
    )


    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                              verbose_name="Usuario creador")
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE,
                                     related_name='activities', verbose_name="Organización")
    description = models.TextField(verbose_name="Descripción")
    start_date = models.DateField(verbose_name="Fecha de inicio")
    end_date = models.DateField(verbose_name="Fecha de fin")
    duration = models.PositiveIntegerField(default=0, verbose_name="Duración en horas",
                                           help_text="Si se deja en 0 y se incluye atenciones la duración en horas se calcula automáticamente")
    manual_edited = models.BooleanField(default=True)
    attention_type = models.IntegerField(default=0, choices=ATYPES)

    def __str__(self):
        return "%s - %s" % (
            self.organization, self.description
        )

    class Meta:
        verbose_name = "Reporte Atencion"
        verbose_name_plural = "Reportes de Atencion"


class Attention(models.Model):
    activity = models.ForeignKey(ActivityReport,on_delete=models.CASCADE,
                                 related_name='attentions')
    start_date = models.DateTimeField( verbose_name="Hora de inicio")
    end_date = models.DateTimeField(verbose_name="Hora de fin")

    class Meta:
        verbose_name = "Atencion"
        verbose_name_plural = "Atenciones"


    def __str__(self):
        return "%s - dates: %s / %s" % (
            self.activity, self.start_date,
            self.end_date
        )


class ReportType(models.Model):
    name = models.CharField(max_length=400)

    def __str__(self):
        return self.name


class Report(models.Model):

    DATA_TYPE = [('numerical', "Numérico"), ('percentaje', 'Porcentual')]

    category = models.ForeignKey(ReportType, on_delete=models.CASCADE, verbose_name="Categoría")
    name = models.CharField(max_length=400, verbose_name="Nombre")
    country = models.ManyToManyField(Country, verbose_name="País", blank=True)
    report_type = models.CharField(max_length=200, verbose_name="Tipo de reporte")
    end_date = models.DateField(null=True, blank=True, verbose_name="Fecha final")
    start_date  = models.DateField(null=True, blank=True, verbose_name="Fecha inicial")
    grafic = models.CharField(max_length=50, verbose_name="Tipo de gráfico")
    extra_form = JSONField(null=True, blank=True)
    info_filters = JSONField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    data_type = models.CharField(max_length=50, choices=DATA_TYPE, default=DATA_TYPE[0], verbose_name="Tipo de dato")

    cache_table = models.TextField(null=True, blank=True)
    cache_grafic = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.name