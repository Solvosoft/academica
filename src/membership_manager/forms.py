from ajax_select.fields import AutoCompleteSelectField
from django import forms
from django.contrib.auth.models import User, Group
from django.urls import reverse
from djgentelella.forms.forms import GTForm
from djgentelella.widgets import core as genwidgets
from djgentelella.widgets import core as widget
from djgentelella.widgets.selects import AutocompleteSelect, AutocompleteSelectMultiple

from membership_core.models import MembershipTemplate, Country, ServiceType, SystemCurrency, RenewalPeriod, ServiceMT
from membership_manager.models import Invoice, ActivityReport
from membership_manager.models import Membership, Service, Organization, \
    Report, ReportType
from membership_manager.reports.registro import REPORTES_TITULOS
from membership_manager.utils import get_contentype_choices


class TemplateWidget(forms.Select):
    class Media:
        js = ('js/membershipform.js',)


class MembInvPaymentsForm(forms.Form):
    option = forms.ChoiceField(choices=(
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('inactive', 'Inactivo')
    ), required=False, widget=forms.RadioSelect(attrs={'class': 'grp-horizontal-list', 'padding': '0x 10px'}), )


class MembershipAddForm(forms.ModelForm):
    organization = AutoCompleteSelectField('orgs', label="Organización", required=False)
    # contact = AutoCompleteSelectField('contacts', label="Contacto", required=False)

    membership_template = forms.ModelChoiceField(
        queryset=MembershipTemplate.objects.filter(state="active"),
        required=False,
        label="Plantilla de membresía",
        widget=TemplateWidget()
    )

    class Meta:
        model = Membership
        fields = '__all__'


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

    def has_changed(self):
        """
           Overriding this, as the initial data passed to the form does not get noticed,
           and so does not get saved, unless it actually changes.
        """
        changed_data = super(ServiceForm, self).has_changed()
        return bool(self.initial or changed_data)


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            "name", "initials", "email", "cellphone", "phone", "country", "province", "city", "address",
            "postal_code", "active", "currency", "payment_method", "identification_type", "identification",
        ]


class ContactOrganizationForm(GTForm, forms.Form):
    organization = forms.ModelChoiceField(widget=genwidgets.Select, queryset=Organization.objects.all(),
                                          label="Buscar contacto", required=True)

    def __init__(self, *args, **kwargs):
        pk = kwargs.pop('pk')
        super().__init__(*args, **kwargs)

        contacts = Organization.objects.filter(pk=pk).first().contacts.all().values_list('pk', flat=True)

        if contacts:
            self.fields['organization'].queryset = Organization.objects.filter(type=True).exclude(pk__in=contacts)


class MembershipForm(GTForm, forms.ModelForm):
    CHOICES = (
        ('organization', 'Organización'),
        ('contact', 'Contacto'),
    )
    contact_type = forms.ChoiceField(
        choices=CHOICES, widget=widget.RadioSelect, label="Tipo de contacto")
    contact = forms.ModelChoiceField(widget=AutocompleteSelect('contactbasename'),
                                     queryset=Organization.objects.filter(type=True), label="Contacto", required=False)

    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)

        self.fields['organization'].label = "Organización"
        self.fields['organization'].required = False
        self.fields['apply_fees'].help_text = "(Al no seleccionar este campo la aplicación de impuestos será ignorada)"

    class Meta:
        model = Membership
        fields = [
            'membership_type', 'contact_type', 'organization', 'contact',
            'annual_cost', 'currency', 'renewal_period', 'state',
            'apply_fees', 'fees', 'free_membership'
        ]
        widgets = {
            'organization': AutocompleteSelect('organizationbasename'),
            'membership_type': widget.Select,
            'currency': widget.Select,
            'annual_cost': widget.NumberInput,
            'renewal_period': widget.Select,
            'apply_fees': widget.YesNoInput,
            'state': widget.Select,
            'fees': forms.NumberInput(attrs={'step': "0.01", "class": "form-control"}),
            'free_membership': widget.YesNoInput
        }

    def clean(self):
        contact_type = self.cleaned_data.get("contact_type")
        organization = self.cleaned_data.get("organization")
        contact = self.cleaned_data.get("contact")
        if contact_type == "organization":
            if organization == "" or organization is None:
                raise forms.ValidationError("Debe seleccionar una organización")
        else:
            if contact == "" or contact is None:
                raise forms.ValidationError("Debe seleccionar un contacto")


class MembershipServiceForm(GTForm, forms.ModelForm):
    class Meta:
        model = Service
        fields = ['servicetype', 'description', 'observations']

        widgets = {
            'servicetype': AutocompleteSelect('servicetypebasename'),
            'description': widget.TextInput,
            'observations': widget.Textarea,
        }


class ReportForm(GTForm, forms.ModelForm):
    name = forms.CharField(widget=widget.TextInput, required=False, label="Nombre")
    category = forms.ModelChoiceField(queryset=ReportType.objects.all(),
                                      required=False,
                                      widget=widget.SelectWithAdd(attrs={'add_url': "#"}), label="Categoría")
    country = forms.ModelMultipleChoiceField(queryset=Country.objects.all(), widget=widget.SelectMultiple,
                                             required=False, label="País")
    start_date = forms.DateField(widget=widget.DateInput, required=False, label="Fecha inicial")
    end_date = forms.DateField(widget=widget.DateInput, required=False, label="Fecha final")
    report_type = forms.ChoiceField(widget=widget.Select, required=True, label="Tipo de reporte")
    grafic = forms.ChoiceField(widget=widget.RadioSelect, choices=(
        ('bar', 'Barras'),
        ('line', 'Lineas'),
        ('pie', 'Circular'),
        ('doughnut', 'Dona')
    ), label="Tipo de gráfico")

    is_saved = forms.IntegerField(widget=forms.HiddenInput)

    def get_is_saved(self, value):
        dev = 0
        if value == '1':
            dev = 1
        return dev

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        self.do_save = 0
        if 'is_saved' in kwargs:
            self.do_save = self.get_is_saved(kwargs.pop('is_saved'))
        super(ReportForm, self).__init__(*args, **kwargs)

        self.fields["report_type"].choices = REPORTES_TITULOS.items()

        if user.has_perm('membership_manager.add_reporttype'):
            self.fields['category'].widget.attrs['add_url'] = reverse('add_reporttype')

        else:
            self.fields['category'] = forms.ModelChoiceField(queryset=ReportType.objects.all(),
                                                             required=False,
                                                             widget=widget.Select, label="Categoría")

        if self.do_save:
            self.fields["name"].required = True
            self.fields["category"].required = True

    class Meta:
        model = Report
        fields = ['name', 'category', 'country', 'report_type', 'end_date', 'start_date', 'grafic',
                  'data_type']
        widgets = {'data_type': widget.RadioSelect}


class CreateReportTypeForm(GTForm, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].label = "Nombre"

    class Meta:
        model = ReportType
        fields = ['name']
        widgets = {
            'name': widget.TextInput
        }


class ContactSearchForm(GTForm, forms.ModelForm):
    contact = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.filter(type=True), widget=widget.SelectMultiple,
        required=False, label="Contacto")
    countries = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all(), widget=widget.SelectMultiple,
        required=False, label="País")

    class Meta:
        model = Organization
        fields = ['contact', 'countries']


class ContactAddForm(GTForm, forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            'name', 'email', 'cellphone',
            'phone', 'country', 'province', 'city', 'address',
            'postal_code', 'active', 'currency', 'payment_method', 'type'
        ]
        widgets = {
            'name': genwidgets.TextInput,
            'email': genwidgets.EmailMaskInput,
            'cellphone': genwidgets.PhoneNumberMaskInput,
            'phone': genwidgets.PhoneNumberMaskInput,
            'address': genwidgets.TextInput,
            'country': AutocompleteSelect('countrybasename'),
            'city': genwidgets.Input,
            'province': genwidgets.Input,
            'postal_code': genwidgets.Input,
            'active': genwidgets.YesNoInput,
            'currency': AutocompleteSelect('currencybasename'),
            'payment_method': widget.Select,
            'type': forms.HiddenInput
        }


class OrganizationSearchForm(GTForm, forms.ModelForm):
    organization = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.filter(type=False), widget=widget.SelectMultiple,
        required=False, label="Organización")
    countries = forms.ModelMultipleChoiceField(
        queryset=Country.objects.all(), widget=widget.SelectMultiple,
        required=False, label="País")

    class Meta:
        model = Organization
        fields = ['organization', 'countries']


class OrganizationAddForm(GTForm, forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            'name', 'initials', 'identification_type',
            'identification', 'email', 'cellphone',
            'phone', 'country', 'province', 'city', 'address',
            'postal_code', 'active', 'currency', 'payment_method',
        ]
        widgets = {
            'name': genwidgets.TextInput,
            'initials': genwidgets.Input,
            'identification_type': genwidgets.Select,
            'identification': genwidgets.TextInput,
            'email': genwidgets.EmailMaskInput,
            'cellphone': genwidgets.PhoneNumberMaskInput,
            'phone': genwidgets.PhoneNumberMaskInput,
            'address': genwidgets.TextInput,
            'country': AutocompleteSelect('countrybasename'),
            'city': genwidgets.Input,
            'province': genwidgets.Input,
            'postal_code': genwidgets.Input,
            'active': genwidgets.YesNoInput,
            'currency': AutocompleteSelect('currencybasename'),
            'payment_method': widget.Select
        }


class MembershipTemplateForm(GTForm, forms.Form):
    template = forms.ModelChoiceField(
        queryset=MembershipTemplate.objects.all(), widget=widget.Select,
        required=False, label="Plantilla de membresía")


class InvoiceChangeForm(GTForm, forms.ModelForm):
    status = forms.ChoiceField(choices=Invoice.STATUS, widget=genwidgets.RadioSelect, label='Estado')
    next = forms.CharField(widget=forms.HiddenInput)
    field_order = ['status', 'amount', 'currency', 'payment_date', 'description',
                   'expiration_date', 'payment_method', 'transaction_number', 'receipt']

    class Meta:
        model = Invoice
        exclude = ['creation_date', 'membership', 'renewal_period', 'code', 'pdf_invoice']
        widgets = {
            'expiration_date': genwidgets.DateInput,
            'payment_date': genwidgets.DateInput,
            # 'membership': genwidgets.ReadOnlySelect,
            # 'renewal_period': genwidgets.ReadOnlySelect,
            'description': genwidgets.Textarea,
            'amount': genwidgets.NumberInput,
            'currency': genwidgets.Select,
            'payment_method': genwidgets.Select,
            'transaction_number': genwidgets.TextInput,
            # 'pdf_invoice': genwidgets.FileInput,
            # 'receipt': genwidgets.FileInput
        }


class InvoicePayForm(GTForm, forms.ModelForm):
    next = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Invoice
        exclude = ['creation_date', 'membership', 'renewal_period', 'code', 'pdf_invoice', 'status',
                   'expiration_date', 'description']
        widgets = {
            'payment_date': genwidgets.DateInput,
            'amount': genwidgets.NumberInput,
            'currency': genwidgets.Select,
            'payment_method': genwidgets.Select,
            'transaction_number': genwidgets.TextInput,
            # 'pdf_invoice': genwidgets.FileInput,
            # 'receipt': genwidgets.FileInput
        }


class ServiceTypeForm(GTForm, forms.ModelForm):
    class Meta:
        model = ServiceType
        fields = '__all__'

        widgets = {
            'name': genwidgets.Input
        }


class ActivityReportForm(GTForm, forms.Form):
    organization = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        widget=genwidgets.SelectMultiple,
        required=False, label="Organizaciones o contactos"
    )
    daterange = forms.CharField(
        widget=genwidgets.DateRangeInput,
        required=False, label='Rango de fechas'
    )


class ActivityReportHours(GTForm, forms.Form):
    start_date = forms.DateTimeField(widget=genwidgets.DateTimeInput)
    end_date = forms.DateTimeField(widget=genwidgets.DateTimeInput)
    item = forms.IntegerField(widget=forms.HiddenInput)


class ActivityReportAddForm(GTForm, forms.ModelForm):
    field_order = ['attention_type', 'organization', 'description', 'start_date', 'end_date', 'duration']

    class Meta:
        model = ActivityReport
        exclude = ['user', 'manual_edited']
        widgets = {
            'organization': genwidgets.Select,
            'description': genwidgets.Textarea,
            'start_date': genwidgets.DateInput,
            'end_date': genwidgets.DateInput,
            'duration': genwidgets.NumberInput,
            'attention_type': genwidgets.RadioHorizontalSelect

        }


class UserSearchForm(GTForm, forms.Form):
    user = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), widget=widget.SelectMultiple,
        required=False, label="Buscar por nombre de usuario")
    group = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), widget=widget.SelectMultiple,
        required=False, label="Grupo")


class UserAddForm(GTForm, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    field_order = ['username', 'first_name', 'last_name', 'email', 'is_active', 'groups']

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'groups']
        widgets = {
            'username': genwidgets.TextInput,
            'first_name': genwidgets.TextInput,
            'last_name': genwidgets.TextInput,
            'email': genwidgets.EmailMaskInput,
            'is_active': genwidgets.YesNoInput,
            'groups': genwidgets.SelectMultiple

        }


class GroupAddForm(GTForm, forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']

        widgets = {
            'name': genwidgets.Input,
            'permissions': genwidgets.SelectMultiple
        }


class TemplateSearchForm(GTForm, forms.Form):
    name = forms.CharField(
        required=False, label="Nombre", widget=widget.TextInput)
    currency = forms.ModelMultipleChoiceField(
        required=False, label="Moneda", widget=widget.SelectMultiple,
        queryset=SystemCurrency.objects.all())
    renewal_period = forms.ModelMultipleChoiceField(
        required=False, label="Período de renovación", widget=widget.SelectMultiple,
        queryset=RenewalPeriod.objects.all())


class TemplateAddForm(GTForm, forms.ModelForm):
    class Meta:
        model = MembershipTemplate
        fields = '__all__'
        widgets = {
            'name': widget.TextInput,
            'membership_type': widget.Select,
            'state': widget.Select,
            'renewal_period': widget.Select,
            'annual_cost': widget.NumberInput,
            'state': widget.Select,
            'currency': widget.Select,
            'description': widget.Textarea,
            'free_membership': widget.YesNoInput
        }


class TemplateServiceAddForm(GTForm, forms.ModelForm):
    class Meta:
        model = ServiceMT
        fields = ['servicetype', 'description', 'observations']

        widgets = {
            'servicetype': AutocompleteSelect('servicetypebasename'),
            'description': widget.TextInput,
            'observations': widget.Textarea,
        }

class LogEntryFilterForm(GTForm, forms.Form):
    category = forms.ChoiceField(widget=genwidgets.Select, choices=get_contentype_choices(), label="Categoría", required=True)


class ContactsForm(GTForm, forms.Form):

    contacts = forms.ModelMultipleChoiceField(widget=AutocompleteSelectMultiple('contactbasename'),
                                  queryset=Organization.objects.filter(type=True), label="Contactos", required=False)