'''
Created on 7/4/2015

@author: luisza
'''

from django import forms
from matricula.models import Student
from django.utils.translation import ugettext_lazy as _


class StudentCreateForm(forms.Form):
    name = forms.CharField(label=_('Your name'), max_length=100)
    email = forms.EmailField()
    
    password = forms.CharField(widget=forms.PasswordInput(), label=_("Password"))
    password_check = forms.CharField(widget=forms.PasswordInput(), label=_("Repeat password"))


    def clean(self):
        cleaned_data = super(StudentCreateForm, self).clean()
        if Student.objects.filter(username=cleaned_data['name']).exists():
            raise forms.ValidationError(_("User name exist "))
        
        if cleaned_data['password'] != cleaned_data['password_check']:
            raise forms.ValidationError(_("Password not match "))
