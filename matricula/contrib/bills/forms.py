# encoding: utf-8

'''
Created on 03/11/2020

@author: allexiusw
'''
from django import forms
from .models import ColonExchange, Bill
from matricula.models import Student, Group
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


class BillSearchForm(GTForm, forms.Form): 
    NOT_PAID = 0
    PAID = 1
    DO_NOT_APPLY = 2

    OPTIONS = (
        (DO_NOT_APPLY, "No filtrar"),
        (NOT_PAID, "Sin pagar"),
        (PAID, "Pagado"),
    )

    student = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(), label="Estudiante", widget=djgentelella.SelectMultiple,
        required=False
    )
    is_paid = forms.ChoiceField(
        choices=OPTIONS, widget=djgentelella.Select, label="Pagado", required=False,
    )


class BillCreateForm(forms.ModelForm, GTForm):  
    class Meta:
        model = Bill
        fields = '__all__'
        widgets = {
            'short_description': djgentelella.TextInput,
            'description': djgentelella.Textarea,
            'amount': djgentelella.NumberInput,
            'student': djgentelella.Select,
            'currency': djgentelella.Select(choices=Group.COURRENCY_CHOICES),
            'is_paid': djgentelella.YesNoInput,
            'transaction_id': djgentelella.Textarea,
        }
    def __init__(self, *args, **kwargs):
        super(BillCreateForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'student_id' in kwargs['initial']:
                self.fields['student'].initial = kwargs['initial']['student_id']
