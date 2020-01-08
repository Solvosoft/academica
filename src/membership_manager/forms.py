from django import forms

from membership_core.models import MembershipTemplate
from membership_manager.models import Membership, Service


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
