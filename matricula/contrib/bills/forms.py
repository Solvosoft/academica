# encoding: utf-8

'''
Created on 03/11/2020

@author: allexiusw
'''
from django import forms
from .models import ColonExchange
from django.utils.translation import ugettext_lazy as _
from djgentelella.widgets import core as djgentelella
from djgentelella.forms.forms import GTForm
from djgentelella.widgets.selects import AutocompleteSelect, SelectMultiple

class ColonExchangeCreateForm(forms.ModelForm, GTForm):  
    class Meta:
        model = ColonExchange
        fields = '__all__'
        widgets = {
            'is_dolar': djgentelella.NumberInput
        }

