from django import forms
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext as _
from django.db.models.expressions import Q

from djgentelella.forms.forms import GTForm
from djgentelella.widgets import core as genwidgets
from djgentelella.widgets import core as widget
from djgentelella.widgets.selects import AutocompleteSelectMultiple

from matricula.models import FakeGroup


class UserSearchForm(GTForm, forms.Form):
    user = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), widget=widget.SelectMultiple,
        required=False, label="Buscar por nombre de usuario")
    fakegroup = forms.ModelMultipleChoiceField(
        queryset=FakeGroup.objects.all(), widget=AutocompleteSelectMultiple('fakegroupsbase'),
        required=False, label="Grupo")


class UserAddForm(GTForm, forms.ModelForm):

    fakegroups = forms.ModelMultipleChoiceField(
        queryset=FakeGroup.objects.all(), widget=AutocompleteSelectMultiple('fakegroupsbase'),
        required=False, label="Grupo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True

    field_order = ['username', 'first_name', 'last_name', 'email', 'is_active', 'fakegroups']

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'fakegroups']
        widgets = {
            'username': genwidgets.TextInput,
            'first_name': genwidgets.TextInput,
            'last_name': genwidgets.TextInput,
            'email': genwidgets.EmailMaskInput,
            'is_active': genwidgets.YesNoInput,
            'groups': genwidgets.SelectMultiple
        }
    
    def clean_email(self):
        dev = self.cleaned_data['email']
        if User.objects.filter(email=dev).exists():
            raise forms.ValidationError(_("This email already used"))
        return dev


class UserEditForm(GTForm, forms.ModelForm):
    fakegroups = forms.ModelMultipleChoiceField(
        queryset=FakeGroup.objects.all(), widget=AutocompleteSelectMultiple('fakegroupsbase'),
        required=False, label="Grupo")

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    field_order = ['username', 'first_name', 'last_name', 'email', 'is_active', 'fakegroups']

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'fakegroups']
        widgets = {
            'username': genwidgets.TextInput,
            'first_name': genwidgets.TextInput,
            'last_name': genwidgets.TextInput,
            'email': genwidgets.EmailMaskInput,
            'is_active': genwidgets.YesNoInput,
            'groups': genwidgets.SelectMultiple
        }

    def clean_email(self):
        dev = self.cleaned_data['email']
        username = self.cleaned_data['username']
        duplicate_fields = User.objects.filter(email=dev)
        duplicate_fields = duplicate_fields.exclude(Q(username=username)|Q(username=self.instance))
        if duplicate_fields.exists():
            raise forms.ValidationError(_("This email already used"))
        return dev


class GroupAddForm(GTForm, forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']

        widgets = {
            'name': genwidgets.Input,
            'permissions': genwidgets.SelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super(GroupAddForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'name' in kwargs['initial']:
                self.fields['name'].initial = kwargs['initial']['name']
