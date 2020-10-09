from ajax_select.fields import AutoCompleteSelectField
from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from djgentelella.forms.forms import GTForm
from djgentelella.widgets import core as widget
from djgentelella.widgets.selects import AutocompleteSelect

from membership_core.models import MembershipTemplate, Country, ServiceType
from membership_manager.models import Membership, Service, Organization,\
    Report, ReportType
from membership_manager.reports.registro import REPORTES_TITULOS
from djgentelella.widgets import core as genwidgets

class TemplateWidget(forms.Select):
    class Media:
        js = ('js/membershipform.js',)


class MembInvPaymentsForm(forms.Form):
    option = forms.ChoiceField(choices=(
        ('pending', 'Pendiente'),
        ('paid','Pagado'),
        ('inactive','Inactivo')
    ),required=False,widget=forms.RadioSelect(attrs={'class': 'grp-horizontal-list','padding':'0x 10px'}),)


class MembershipAddForm(forms.ModelForm):

    organization=AutoCompleteSelectField('orgs', label="Organización", required=False)
    contact = AutoCompleteSelectField('contacts', label="Contacto", required=False)

    membership_template = forms.ModelChoiceField(
        queryset=MembershipTemplate.objects.filter(state="active"),
        required=False,
        label="Plantilla de membresía",
        widget=TemplateWidget()
    )

    class Meta:
        model = Membership
        fields = '__all__'

    def clean(self):
        cleaned_data = super(MembershipAddForm, self).clean()
        organization = cleaned_data.get("organization")
        contact = cleaned_data.get("contact")

        if organization or contact :
            return  cleaned_data
        else:
            raise forms.ValidationError("Debe ingresar una organización o contacto.")

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

    organization = forms.ModelChoiceField(widget=genwidgets.Select, queryset=Organization.objects.all(), label="Buscar contacto", required=True)

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
        self.initial['contact_type'] = 'organization'


    class Meta:
        model = Membership
        fields = [
            'membership_type', 'contact_type', 'organization', 'contact',
            'annual_cost', 'currency', 'renewal_period', 'state',
            'apply_fees', 'fees'
        ]
        widgets = {
            'organization': AutocompleteSelect('organizationbasename'),
            'membership_type': widget.Select,
            'currency': widget.Select,
            'annual_cost': widget.NumberInput,
            'renewal_period': widget.Select,
            'apply_fees': widget.YesNoInput,
            'state': widget.Select,
            'fees': widget.NumberInput
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
    country = forms.ModelMultipleChoiceField(queryset=Country.objects.all(), widget=widget.SelectMultiple, required=False, label="País")
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
            'name': forms.TextInput
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
            'email': genwidgets.EmailInput,
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
            'phone', 'address', 'country', 'province', 'city',
            'postal_code', 'active', 'currency', 'payment_method',
        ]
        widgets = {
            'name': genwidgets.TextInput,
            'initials': genwidgets.Input,
            'identification_type': genwidgets.Select,
            'identification': genwidgets.TextInput,
            'email': genwidgets.EmailInput,
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


class ServiceTypeForm(GTForm, forms.ModelForm):

    class Meta:
        model = ServiceType
        fields = '__all__'

        widgets = {
            'name': genwidgets.Input
        }