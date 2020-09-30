from ajax_select.fields import AutoCompleteSelectField
from django import forms
from django.core.exceptions import ValidationError
from membership_core.models import MembershipTemplate
from membership_manager.models import Membership, Service, Organization
from djgentelella.forms.forms import GTForm
from djgentelella.widgets import core as widget
from djgentelella.widgets.selects import AutocompleteSelect


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
    contact = AutoCompleteSelectField('contacts', label="Contacto", required=False)

    class Meta:
        model = Organization
        fields = [
            "name",
            "initials",
            "contact",
            "email",
            "cellphone",
            "phone",
            "address",
            "country",
            "city",
            "province",
            "postal_code",
            "active",
            "currency",
            "payment_method",
            "identification_type",
            "identification",
        ]


class MembershipForm(GTForm, forms.ModelForm):
    ORGANIZATION = 'organization'
    CONTACT = 'contact'
    BOTH = "both"
    CHOICES = (
        (ORGANIZATION, 'Organización'),
        (CONTACT, 'Contacto'),
        (BOTH, 'Ambos'),
    )
    contact_type = forms.ChoiceField(
        choices=CHOICES, widget=widget.RadioSelect, label="Tipo de Contacto")

    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
        # assign a (computed, I assume) default value to the choice field
        self.initial['contact_type'] = self.ORGANIZATION
        if 'initial' in kwargs:
            self.fields['annual_cost'].initial = kwargs['initial']['annual_cost']
            self.fields['currency'].initial = kwargs['initial']['currency_id']
            self.fields['renewal_period'].initial = kwargs['initial']['renewal_period_id']
            if 'apply_fees' in kwargs['initial']:
                self.fields['apply_fees'].initial = kwargs['initial']['apply_fees']
            if 'contact_id' in kwargs['initial']:
                self.fields['contact'].initial = kwargs['initial']['contact_id']
            if 'contact_id' in kwargs['initial']:
                self.fields['organization'].initial = kwargs['initial']['organization_id']

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
            'contact': AutocompleteSelect('contactbasename'),
            'currency': widget.Select,
            'annual_cost': widget.NumberInput,
            'renewal_period': widget.Select,
            'apply_fees': widget.YesNoInput,
            'state': widget.Select,
            'fees': widget.NumberInput
        }

    def clean_organization(self):
        contact_type = self.cleaned_data.get("contact_type", None)
        organization = self.cleaned_data.get("organization", None)
        if contact_type == MembershipForm.BOTH:
            if organization == "" or organization is None:
                raise ValidationError("Olvido seleccionar una 'organización'")
        elif contact_type == MembershipForm.ORGANIZATION:
            if organization == "" or organization is None:
                raise ValidationError("Olvido seleccionar una 'organización'")
        return organization

    def clean_contact(self):
        contact_type = self.cleaned_data.get("contact_type", None)
        contact = self.cleaned_data.get("contact", None)
        if contact_type == MembershipForm.BOTH:
            if contact == "" or contact is None:
                raise ValidationError("Olvido seleccionar un 'contacto'")
        elif contact_type == MembershipForm.CONTACT:
            if contact == "" or contact is None:
                raise ValidationError("Olvido seleccionar un 'contacto'")
        return contact

    def clean_fees(self):
        apply_fees = self.cleaned_data.get("apply_fees", None)
        fees = self.cleaned_data.get("fees", None)
        if apply_fees == 'off':
            fees = 0
        return fees


class MembershipServiceForm(GTForm, forms.ModelForm):
    class Meta:
        model = Service
        fields = ['servicetype', 'description', 'observations']

        widgets = {
            'servicetype': AutocompleteSelect('servicetypebasename'),
            'description': widget.TextInput,
            'observations': widget.Textarea,
        }

        def __init__(self, *args, **kwargs):
            super(MembershipServiceForm, self).__init__(*args, **kwargs)
            # assign a (computed, I assume) default value to the choice field
