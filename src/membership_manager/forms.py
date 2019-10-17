from django import forms

from membership_core.models import MembershipTemplate
from membership_manager.models import Membership


class TemplateWidget(forms.Select):
    class Media:
        js = ('js/membershipform.js',)

class MembInvPaymentsForm(forms.Form):
    option = forms.ChoiceField(choices=(
        ('pending', 'Pendiente'),
        ('paid','Pagado'),
        ('inactive','Inactivo')
    ),required=False,widget=forms.RadioSelect,)


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

