# encoding: utf-8

'''
Created on 7/4/2015

@author: luisza
'''

from django import forms
from matricula.models import Student, Page, MenuItem
from django.utils.translation import ugettext_lazy as _
from django.core import validators


class StudentCreateForm(forms.Form):
    name = forms.CharField(label=_('Your username'), max_length=30,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ], required=True)
    
    first_name = forms.CharField(label=_('first name'), max_length=30, required=True)
    last_name = forms.CharField(label=_('last name'), max_length=30, required=True)
    
    email = forms.EmailField(required=True)

    password = forms.CharField(widget=forms.PasswordInput(), required=True, label=_("Password"))
    password_check = forms.CharField(widget=forms.PasswordInput(), required=True, label=_("Repeat password"))



    def clean(self):
        cleaned_data = super(StudentCreateForm, self).clean()
        if Student.objects.filter(username=cleaned_data.get('name')).exists():
            raise forms.ValidationError(_("User name exist "))

        if cleaned_data.get('password') != cleaned_data.get('password_check'):
            raise forms.ValidationError(_("Password not match "))


class MenuItemFormPage(forms.ModelForm):
    name = forms.ModelChoiceField(queryset=Page.objects.all(), label=_("Page"))

    def __init__(self, *args, **kwargs):
        super(MenuItemFormPage, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['name'] = forms.ModelChoiceField(queryset=Page.objects.all(), label=_("Page"), initial=kwargs['instance'].name)

    def save(self, *args, **kwargs):
        dev = super(MenuItemFormPage, self).save(*args, **kwargs)
        dev.name = self.cleaned_data['name'].pk
        return dev

    class Meta:
        model = MenuItem
        exclude = ("name",)
        fields = ["name", 'type', 'description', 'require_authentication',
                  'order', 'parent', 'publicated', 'is_index']
