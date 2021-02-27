from django import forms
from django.contrib.auth.models import User, Group
from djgentelella.forms.forms import GTForm
from djgentelella.widgets import core as genwidgets
from djgentelella.widgets import core as widget


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
