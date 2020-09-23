from ajax_select.fields import AutoCompleteSelectField
from django import forms
from membership_core.models import MembershipTemplate
from membership_manager.models import Membership, Service, Organization
from djgentelella.forms.forms import GTForm
from djgentelella.widgets import core as widget


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
    class Meta:
        model = Membership
        fields = [
            'organization', 'membership_type', 'contact', 'annual_cost',
            'currency', 'renewal_period', 'apply_fees', 'state',
            'fees'
        ]
        widgets = {
            'organization': widget.Select,
            'membership_type': widget.Select,
            'contact': widget.Select,
            'currency': widget.Select,
            'renewal_period': widget.Select,
            'apply_fees': widget.YesNoInput,
            'state': widget.Select,
        }
