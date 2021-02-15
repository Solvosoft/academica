# encoding: utf-8

'''
Created on 03/11/2020

@author: allexiusw
'''
from django import forms
from .models import Bill
from matricula.models import Student, Group
from djgentelella.widgets import core as djgentelella
from djgentelella.forms.forms import GTForm
from djgentelella.widgets import tinymce
from membership_core.models import SystemCurrency


class ColonExchangeSearchForm(GTForm, forms.Form):
    rates = forms.CharField(
        required=False, widget=djgentelella.TextInput,
        label="Monto")
    currency = forms.ModelMultipleChoiceField(
        queryset=SystemCurrency.objects.all(), label="Moneda",
        required=False, widget=djgentelella.SelectMultiple)


class ColonExchangeCreateForm(forms.ModelForm, GTForm):
    class Meta:
        model = SystemCurrency
        fields = '__all__'
        widgets = {
            'currency': djgentelella.Select,
            'rates': djgentelella.TextInput
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
        label="Pagado", widget=djgentelella.YesNoInput, required=False)
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
            'description': tinymce.EditorTinymce,
            'amount': djgentelella.NumberInput,
            'currency': djgentelella.Select(choices=Group.COURRENCY_CHOICES),
            'student': djgentelella.Select,
        }

    def __init__(self, *args, **kwargs):
        super(BillCreateForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'student_id' in kwargs['initial']:
                self.fields['student'].initial = kwargs['initial']['student_id']
            if 'currency_id' in kwargs['initial']:
                self.fields['currency'].initial = kwargs['initial']['currency_id']
