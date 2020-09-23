from async_notifications.interfaces import NewsLetterInterface
from async_notifications.models import NewsLetterTemplate, NewsLetter
from async_notifications.settings import NEWSLETTER_WIDGET
from django import forms
from djgentelella.forms.forms import CustomForm
from djgentelella.widgets import core as genwidgets
from djgentelella.widgets.tagging import EmailTaggingInput

from membership_core.models import SystemCurrency, ServiceType, Country
from membership_manager.models import Organization, Membership, PAYMENT, IDS_TYPE, Invoice
from membership_manager.utils import get_context_news_letter
import datetime
from froala_editor.widgets import FroalaEditor


def get_countries_en_membresias():
    keys = Country.objects.all().values('id', 'name')

    for x in keys:
        yield (x['id'], x['name'])



class MembershipFilterForm(forms.Form):
    ACTIVE_CHOICE = (
        (None, "Todas"),
        (1, "Activas"),
        (2, "Inactivas")
    )
    FEE_CHOICE = (
        (None, "Todas"),
        (1, "Con impuestos"),
        (0, "Sin impuestos")
    )

    BUSQUEDA_EN = (
        (None, "Ambos"), (1, "Contacto"), (1, "Organizaciones")
    )

    FACTURAS = ( ("", "Todas"),
        ('1', "Con facturas pendientes"),
        ("2", "Sin pendientes"),

    )

    active = forms.ChoiceField(choices=ACTIVE_CHOICE, required=False)
    country = forms.MultipleChoiceField(choices=get_countries_en_membresias, required=False)
    currency = forms.ModelMultipleChoiceField(SystemCurrency.objects.all(), required=False)
    payment_method = forms.MultipleChoiceField(choices=PAYMENT, required=False)
    apply_fees = forms.ChoiceField(choices=FEE_CHOICE, required=False)
    invoices = forms.ChoiceField(choices=FACTURAS, required=False)
    excludeemail = forms.CharField(widget=forms.HiddenInput, required=False)
    busqueda_en = forms.ChoiceField(choices=BUSQUEDA_EN, required=False)
    service_type = forms.ModelMultipleChoiceField(queryset=ServiceType.objects.all(), required=False)
    membership_type = forms.MultipleChoiceField(choices=[(None, "Todas")]+list(Membership.TYPES), required=False)

class MembershipManager(NewsLetterInterface):
    name = "membresia"
    model = Membership
    form = MembershipFilterForm

    field_map = {
        'exclude': { 'excludeemail': 'organization__email__in'},
        'filter': {
            'active': 'state',
            'country': 'organization__country__in',
            'currency': 'organization__currency__in',
            'payment_method': 'organization__payment_method__in',
            'apply_fees': 'apply_fees',
            'membership_type': 'membership_type__in',
            'service_type': 'service__servicetype__in'
        }
    }


    def get_exclude(self):
        exclude = {}
        self.excludedata=set()
        excludeemail = self.form.cleaned_data['excludeemail']
        if excludeemail:
            e = excludeemail.replace(" ", '').split(',')
            if not e[0]:
                e.pop(0)
            self.excludedata = set(e)
        return exclude

    def get_emails(self):
        mails = []
        busqueda = self.form.cleaned_data.get('busqueda_en', '0')
        if not busqueda:
            busqueda='0'
        if busqueda == '0' or busqueda == '2':
            mails += list(self.queryset.exclude(organization__email__isnull=True).values_list('organization__email', flat=True))
        if busqueda == '0' or busqueda == '1':
            mails += list(self.queryset.exclude(contact__email__isnull=True).values_list('contact__email', flat=True))
        return list(set(mails)-self.excludedata)


    def get_emails_instance(self):
        mails = []
        pks_used = []
        busqueda = self.form.cleaned_data.get('busqueda_en', '0')
        if not busqueda:
            busqueda='0'
        if busqueda == '0' or busqueda == '2':
            mails += list(self.queryset.exclude(organization__email__isnull=True).values_list('organization__email', 'pk'))
        if busqueda == '0' or busqueda == '1':
            mails += list(self.queryset.exclude(contact__email__isnull=True).values_list('contact__email', 'pk'))
        for item in mails:
            pk, email = item[1], item[0]
            key = str(pk)+"_"+email
            if email not in self.excludedata and key not in pks_used:
                yield self.model.objects.filter(pk=pk).first(), email
                pks_used.append(key)


class OrganizationFilterForm(forms.Form):
    ACTIVE_CHOICE = (
        (None, "Todas"),
        (1, "Activas"),
        (0, "Inactivas")
    )
    active = forms.ChoiceField(choices=ACTIVE_CHOICE, required=False)
    country = forms.MultipleChoiceField(choices=get_countries_en_membresias, required=False)
    currency = forms.ModelMultipleChoiceField(SystemCurrency.objects.all(), required=False)
    payment_method = forms.MultipleChoiceField(choices=PAYMENT, required=False)
    identification_type = forms.MultipleChoiceField(choices=IDS_TYPE, required=False)
    excludeemail = forms.CharField(widget=forms.HiddenInput, required=False)

class OrganizationManager(NewsLetterInterface):
    name = "organizacion"
    model = Organization
    form = OrganizationFilterForm
    field_map ={
        'exclude': { 'excludeemail': 'email__in'},
        'filter': {
            'active': 'active',
            'country': 'country__in',
            'currency': 'currency__in',
            'payment_method': 'payment_method__in',
            'identification_type': 'identification_type__in'
        }
    }

    def get_emails(self):
        return list(set(self.queryset.exclude(email__isnull=True).values_list('email', flat=True)))

    def get_emails_instance(self):
        pks_used=[]
        mails = self.queryset.exclude(email__isnull=True).values_list('email', 'id')
        for item in mails:
            pk, email = item[1], item[0]
            key = str(pk) + "_" + email
            if email not in self.excludedata and key not in pks_used:
                yield self.model.objects.filter(pk=pk).first(), email
                pks_used.append(key)

class InvoiceFilterForm(forms.Form):
    ACTIVE_CHOICE = (
        (None, "Todas"),
        (1, "Activas"),
        (0, "Inactivas")
    )
    FEE_CHOICE = (
        (None, "Todas"),
        (1, "Con impuestos"),
        (0, "Sin impuestos")
    )

    BUSQUEDA_EN = (
        (None, "Ambos"), (1, "Contacto"), (1, "Organizaciones")
    )

    STATUS = ( ("", "Todas"),
        ('pending', "Pendiente"),
        ("paid", "Pagada"),
        ("inactive", "Inactiva")
    )

    active = forms.ChoiceField(choices=ACTIVE_CHOICE, required=False)
    country = forms.MultipleChoiceField(choices=get_countries_en_membresias, required=False)
    currency = forms.ModelMultipleChoiceField(SystemCurrency.objects.all(), required=False)
    payment_method = forms.MultipleChoiceField(choices=PAYMENT, required=False)
    apply_fees = forms.ChoiceField(choices=FEE_CHOICE, required=False)
    status = forms.ChoiceField(choices=STATUS, required=False)
    expiration_start_date = forms.DateField(widget=forms.DateInput, required=False)
    expiration_end_date = forms.DateField(widget=forms.DateInput, required=False)
    excludeemail = forms.CharField(widget=forms.HiddenInput, required=False)
    busqueda_en = forms.ChoiceField(choices=BUSQUEDA_EN, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expiration_start_date'].widget.input_type = 'date'
        self.fields['expiration_end_date'].widget.input_type = 'date'

class InvoiceManager(NewsLetterInterface):
    name = "factura"
    model = Invoice
    form = InvoiceFilterForm

    field_map = {
        'exclude': { 'excludeemail': 'membership__organization__email__in'},
        'filter': {
            'active': 'membership__state',
            'country': 'membership__organization__country__in',
            'currency': 'currency__in',
            'payment_method': 'payment_method__in',
            'apply_fees': 'membership__apply_fees',
            'status': 'status',
            'expiration_start_date': 'expiration_date__gte',
            'expiration_end_date': 'expiration_date__lte'
        }
    }

    def get_exclude(self):
        exclude = {}
        self.excludedata=set()
        excludeemail = self.form.cleaned_data['excludeemail']
        if excludeemail:
            e = excludeemail.replace(" ", '').split(',')
            if not e[0]:
                e.pop(0)
            self.excludedata = set(e)
        return exclude

    def get_emails(self):
        mails = []
        busqueda = self.form.cleaned_data.get('busqueda_en', '0')
        if not busqueda:
            busqueda='0'
        if busqueda == '0' or busqueda == '2':
            mails += list(self.queryset.exclude(membership__organization__email__isnull=True).values_list('membership__organization__email', flat=True))
        if busqueda == '0' or busqueda == '1':
            mails += list(self.queryset.exclude(membership__contact__email__isnull=True).values_list('membership__contact__email', flat=True))
        return list(set(mails)-self.excludedata)

    def get_emails_instance(self):
        mails = []
        pks_used = []
        busqueda = self.form.cleaned_data.get('busqueda_en', '0')
        if not busqueda:
            busqueda = '0'
        if busqueda == '0' or busqueda == '2':
            mails += list(self.queryset.exclude(membership__organization__email__isnull=True).values_list('membership__organization__email', 'id'))
        if busqueda == '0' or busqueda == '1':
            mails += list(self.queryset.exclude(membership__contact__email__isnull=True).values_list('membership__contact__email', 'id'))
        for item in mails:
            pk, email = item[1], item[0]
            key = str(pk) + "_" + email
            if email not in self.excludedata and key not in pks_used:
                yield self.model.objects.filter(pk=pk).first(), email
                pks_used.append(key)


class NewsLetterTemplateForm(CustomForm, forms.Form):

    news_letter_template = forms.ModelChoiceField(widget=genwidgets.Select, queryset=NewsLetterTemplate.objects.all(),
                                                  required=True, label="Plantilla de boletín")


class NewsLetterForm(CustomForm, forms.ModelForm):
    templatecontext = forms.ChoiceField(widget=genwidgets.Select, choices=[], label="Contexto")

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super().__init__(*args, **kwargs)

        self.fields['templatecontext'].choices = get_context_news_letter(pk)

    field_order = ['template', 'subject', 'templatecontext', 'message', 'recipient', 'file', 'creator', 'filters' ]

    class Meta:
        model = NewsLetter
        exclude = ['cc', 'bcc']
        widgets = {
            'template': forms.HiddenInput,
            'subject': genwidgets.TextInput,
            'message':  FroalaEditor,
            'recipient': EmailTaggingInput,
            'creator': forms.HiddenInput,
            'filters': forms.HiddenInput,
            'file': genwidgets.FileInput
        }

    class Media:
        js = ['js/newsletter.js']

class FilterEmailsForm(CustomForm, forms.Form):

    MEMBERSHIP_STATES = (
        (None, "Todas"),
        ("active", "Activas"),
        ("inactive", "Inactivas"),
    )
    MEMBERSHIP_TYPES = (("Personal", "Personal"),
             ("Radial", "Radial"),
             ("Organizacional", "Organizacional"),
             ("Global", "Global"),
             ("Honoraria", "Honoraria"),
             ('Básica', 'Básica'))

    PAYMENT_METHOD = (
        ("Cash", "Efectivo"),
        ("Bank transfer", "Transferencia bancaria"),
        ("Paypal", "Paypal"),
        ("Bitcoins", "Bitcoins"),
        ('MoneyGram', 'MoneyGram'),
        ('WesterUnion', 'WesterUnion'),
        ('Transferencia Bancaria Argentina', 'Transferencia Bancaria Argentina')
    )

    APPLY_FEES = (
        (None, "Todas"),
        (True, "Con impuestos"),
        (False, "Sin impuestos"),
    )

    INVOICES_CHOICES = (
        (None, "Todas"),
        ("pending", "Con facturas pendientes"),
        ("paid", "Sin pendientes"),
    )

    SEARCH_IN_CHOICES = (
        (None, "Ambos"),
        ("contacto", "Contacto"),
        ("organizacion", "Organizacion"),
    )

    apply_filters = forms.BooleanField(widget=genwidgets.YesNoInput, required=False, label="¿Desea aplicar filtros?")
    state = forms.ChoiceField(widget=genwidgets.Select, choices=MEMBERSHIP_STATES, required=False, label="Estado")
    country = forms.ModelMultipleChoiceField(widget=genwidgets.SelectMultiple, queryset=Country.objects.all(), required=False, label="País")
    currency = forms.ModelChoiceField(widget=genwidgets.SelectMultiple, queryset=SystemCurrency.objects.all(), required=False, label="Moneda")
    payment_method = forms.MultipleChoiceField(widget=genwidgets.SelectMultiple, choices=PAYMENT_METHOD, required=False, label="Método de pago")
    apply_fees = forms.ChoiceField(widget=genwidgets.Select, choices=APPLY_FEES, required=False, label="Tarifas aplicadas")
    invoices = forms.ChoiceField(widget=genwidgets.Select, choices=INVOICES_CHOICES, required=False, label="Facturas")
    search_in = forms.ChoiceField(widget=genwidgets.Select, choices=SEARCH_IN_CHOICES, required=False, label="Búsqueda en")
    service_type = forms.ModelChoiceField(widget=genwidgets.SelectMultiple, queryset=ServiceType.objects.all(), required=False, label="Tipo de servicio")
    membership_type = forms.MultipleChoiceField(widget=genwidgets.SelectMultiple, choices=MEMBERSHIP_TYPES, required=False, label="Tipo de membresía")


class SendDateForm(CustomForm, forms.Form):

    send_date = forms.DateTimeField(widget=genwidgets.DateTimeInput, required=True, label="Fecha y hora de envío",
                                          help_text="La fecha y hora ingresada no debe ser inferior a la fecha y hora actual.")

    def clean(self):

        cleaned_data = super(SendDateForm, self).clean()
        current_date = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        send_date = cleaned_data.get("send_date").strftime("%d/%m/%Y, %H:%M:%S")
        if send_date > current_date:
            return cleaned_data
        else:
            raise forms.ValidationError("La fecha y hora ingresada no debe ser inferior a la fecha y hora actual.")



class EmailsNewsLetter(CustomForm, forms.Form):

    emails = forms.CharField(widget=EmailTaggingInput, label="Correos", required=False)