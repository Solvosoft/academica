# encoding: utf-8

'''
Created on 7/4/2015

@author: luisza
'''
from django import forms
from matricula.models import Student, Page, MenuItem, Category, Course
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.contrib.auth.models import User
from djgentelella.widgets import core as djgentelella
from djgentelella.widgets import wysiwyg as widget
from djgentelella.forms.forms import GTForm
from djgentelella.widgets.selects import AutocompleteSelect, SelectMultiple


class StudentCreateForm(GTForm, forms.ModelForm):
    name = forms.CharField(label=_('Your username'), max_length=30,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                                      _('Enter a valid username. '
                                        'This value may contain only letters, numbers '
                                        'and @/./+/-/_ characters.'), 'invalid'),
        ], required=True)
    
    first_name = forms.CharField(
        label=_('first name'), max_length=30, required=True,
        widget=djgentelella.TextInput)
    last_name = forms.CharField(label=_('last name'), max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True, label=_("Password"))
    password_check = forms.CharField(widget=forms.PasswordInput(), required=True, label=_("Repeat password"))

    class Meta:
        widgets = {
            'last_name': djgentelella.TextInput,
            'email': djgentelella.EmailInput
        }


    def clean(self):
        cleaned_data = super(StudentCreateForm, self).clean()
        if User.objects.filter(username=cleaned_data.get('name')).exists():
            raise forms.ValidationError(_("User name exist "))

        if cleaned_data.get('password') != cleaned_data.get('password_check'):
            raise forms.ValidationError(_("Password not match "))



class StudentEditForm(GTForm, forms.ModelForm):  
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email']
        widgets = {
            'last_name': djgentelella.TextInput,
            'first_name': djgentelella.TextInput,
            'email': djgentelella.EmailInput,
        }


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


class CategoryCreateForm(forms.ModelForm, GTForm):  
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': djgentelella.TextInput(attrs={'placeholder':"Nombre categoría"}),
            'description': widget.TextareaWysiwyg,
        }


class CategorySearchForm(forms.ModelForm, GTForm):  
    name = forms.CharField(
        label='Término de búsqueda', required=False,
            widget=djgentelella.TextInput(attrs={
                'placeholder':"Ingrese el término de búsqueda",
            }
        )
    )
    class Meta:
        model = Category
        fields = ['name']


class CourseSearchForm(forms.ModelForm, GTForm):  
    name = forms.CharField(
        label='Término de búsqueda', required=False,
        widget=djgentelella.TextInput(
            attrs={
                'placeholder':"Ingrese el término de búsqueda",
            })
    )
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Categoría")
    class Meta:
        model = Course
        fields = ['name','category']


class CourseCreateForm(forms.ModelForm, GTForm):  
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'name': djgentelella.TextInput(attrs={'placeholder':"Nombre curso"}),
            'content': widget.TextareaWysiwyg,
            'category': AutocompleteSelect('categorybasename'),
        }

    def __init__(self, *args, **kwargs):
        super(CourseCreateForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'category_id' in kwargs['initial']:
                self.fields['category'].initial = kwargs['initial']['category_id']


class MenuItemSearchForm(GTForm, forms.ModelForm):  
    parent = forms.ModelMultipleChoiceField(
        queryset=MenuItem.objects.all(), required=False,
        widget=djgentelella.SelectMultiple
    )

    class Meta:
        model = MenuItem
        fields = ['name']

        widgets = {
            'name': djgentelella.TextInput
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required=False