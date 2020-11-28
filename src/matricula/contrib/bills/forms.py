# encoding: utf-8

'''
Created on 03/11/2020

@author: allexiusw
'''
from django import forms
from .models import ColonExchange, Bill
from matricula.models import Student, Group
from djgentelella.widgets import core as djgentelella
from djgentelella.forms.forms import GTForm


class ColonExchangeSearchForm(GTForm, forms.Form):
    is_dolar = forms.CharField(
        required=False, widget=djgentelella.TextInput,
        label="Monto")


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
        queryset=Student.objects.all(), label="Estudiante",
        widget=djgentelella.SelectMultiple, required=False
    )
    is_paid = forms.ChoiceField(
        choices=OPTIONS, widget=djgentelella.Select, label="Pagado",
        required=False,
    )


class BillCreateForm(forms.ModelForm, GTForm):
    is_paid = forms.CharField(
        label="Pagado", widget=djgentelella.YesNoInput)
    transaction_id = forms.CharField(
        widget=djgentelella.Textarea, label="Id de transacción")

    class Meta:
        model = Bill
        fields = [
                'short_description', 'description', 'amount', 'currency',
                'student', 'is_paid', 'transaction_id'
            ]
        widgets = {
            'short_description': djgentelella.TextInput,
            'description': djgentelella.Textarea,
            'amount': djgentelella.NumberInput,
            'currency': djgentelella.Select(choices=Group.COURRENCY_CHOICES),
            'student': djgentelella.Select,
        }

    def __init__(self, *args, **kwargs):
        super(BillCreateForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'student_id' in kwargs['initial']:
                self.fields['student'].initial = kwargs['initial']['student_id']
