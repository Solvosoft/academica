# encoding: utf-8

'''
Created on 7/4/2015

@author: luisza
'''
from django import forms
from matricula.models import Student, Page, MenuItem, Category, Course,\
    Period, Group, Enroll
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.contrib.auth.models import User
from djgentelella.widgets import core as djgentelella
from djgentelella.widgets import wysiwyg as widget
from djgentelella.forms.forms import GTForm
from djgentelella.widgets.selects import AutocompleteSelect


class StudentCreateForm(GTForm, forms.ModelForm):
    name = forms.CharField(
        label=_('Your username'), max_length=30,
        help_text=_('Required. 30 characters or fewer. Letters, digits and '
                    '@/./+/-/_ only.'),
        validators=[
            validators.RegexValidator(r'^[\w.@+-]+$',
                _('Enter a valid username. '
                    'This value may contain only letters, numbers '
                    'and @/./+/-/_ characters.'), 'invalid'),
        ], required=True, widget=djgentelella.TextInput)
    first_name = forms.CharField(
        label=_('first name'), max_length=30, required=True,
        widget=djgentelella.TextInput)
    last_name = forms.CharField(
        label=_('last name'), max_length=30, required=True,
        widget=djgentelella.TextInput)
    email = forms.EmailField(required=True, widget=djgentelella.EmailMaskInput)
    password = forms.CharField(
        required=True, label=_("Password"), widget=djgentelella.PasswordInput)
    password_check = forms.CharField(
        widget=djgentelella.PasswordInput, required=True,
        label=_("Repeat password"))

    class Meta:
        model = Student
        fields = [
            'name', 'first_name', 'last_name', 'email',
            'password', 'password_check']
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
            self.fields['name'] = forms.ModelChoiceField(
                queryset=Page.objects.all(), label=_("Page"),
                initial=kwargs['instance'].name)

    def save(self, *args, **kwargs):
        dev = super(MenuItemFormPage, self).save(*args, **kwargs)
        dev.name = self.cleaned_data['name'].pk
        return dev

    class Meta:
        model = MenuItem
        exclude = ("name",)
        fields = [
            "name", 'type', 'description', 'require_authentication',
            'order', 'parent', 'publicated', 'is_index']


class CategoryCreateForm(forms.ModelForm, GTForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': djgentelella.TextInput,
            'description': djgentelella.Textarea,
        }


class CategorySearchForm(GTForm, forms.Form):
    name = forms.CharField(
        label='Término de búsqueda', required=False,
        widget=djgentelella.TextInput)


class CourseSearchForm(GTForm, forms.Form):
    name = forms.CharField(
        label='Término de búsqueda', required=False,
        widget=djgentelella.TextInput)
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Categoría")


class CourseCreateForm(forms.ModelForm, GTForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'name': djgentelella.TextInput(
                attrs={'placeholder': "Nombre curso"}),
            'content': widget.TextareaWysiwyg,
            'category': AutocompleteSelect('categorybasename'),
        }

    def __init__(self, *args, **kwargs):
        super(CourseCreateForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'category_id' in kwargs['initial']:
                self.fields['category'].initial = kwargs['initial']['category_id']


class GroupAddForm(forms.ModelForm, GTForm):
    schedule = forms.CharField(
        required=False, max_length=250, widget=djgentelella.TextInput)

    class Meta:
        model = Group
        fields = [
            'name', 'schedule', 'pre_enroll_start', 'pre_enroll_finish',
            'enroll_start', 'enroll_finish', 'is_paid', 'currency', 'cost',
            'maximum', 'is_open', 'flow'
        ]
        widgets = {
            "name": djgentelella.TextInput,
            "schedule": djgentelella.TextInput,
            "pre_enroll_start": djgentelella.DateTimeInput,
            "pre_enroll_finish": djgentelella.DateTimeInput,
            "enroll_start": djgentelella.DateTimeInput,
            "enroll_finish": djgentelella.DateTimeInput,
            'is_paid': djgentelella.YesNoInput(
                attrs={'rel': ['currency', 'cost']}),
            "currency": djgentelella.Select,
            "cost": djgentelella.NumberInput,
            "maximum": djgentelella.NumberInput,
            "is_open": djgentelella.YesNoInput,
            "flow": djgentelella.Select
        }


class MenuItemSearchForm(GTForm, forms.Form):
    name = forms.CharField(
        required=False, widget=djgentelella.TextInput,
        label="Nombre")
    parent = forms.ModelMultipleChoiceField(
        queryset=MenuItem.objects.all(), required=False,
        widget=djgentelella.SelectMultiple, label="Padre"
    )
    type = forms.MultipleChoiceField(
        choices=MenuItem.TYPES, required=False,
        widget=djgentelella.SelectMultiple, label="Tipo"
    )


class MenuItemCreateForm(forms.ModelForm, GTForm):
    class Meta:
        model = MenuItem
        fields = '__all__'
        widgets = {
            'name': djgentelella.TextInput,
            'type': djgentelella.Select,
            'description': djgentelella.Textarea,
            'require_authentication': djgentelella.YesNoInput,
            'order': djgentelella.NumberInput,
            'parent': djgentelella.Select,
            'publicated': djgentelella.YesNoInput,
            'is_index': djgentelella.YesNoInput
        }


class PeriodSearchForm(GTForm, forms.Form):
    name = forms.CharField(
        required=False, widget=djgentelella.TextInput,
        label="Nombre")


class PeriodCreateForm(forms.ModelForm, GTForm):
    class Meta:
        model = Period
        fields = '__all__'
        widgets = {
            'name': djgentelella.TextInput,
            'start_date': djgentelella.DateInput,
            'finish_date': djgentelella.DateInput
        }

    def clean(self):
        start_date = self.cleaned_data.get("start_date")
        finish_date = self.cleaned_data.get("finish_date")
        if finish_date < start_date:
            msg = u"La fecha final es menor a la inicial"
            self._errors["finish_date"] = self.error_class([msg])


class GroupSearchForm(GTForm, forms.Form):
    OPEN = 0
    CLOSE = 1
    DO_NOT_APPLY = 2

    OPTIONS = (
        (DO_NOT_APPLY, "No aplicar"),
        (OPEN, "Abierto"),
        (CLOSE, "Cerrado"),
    )
    period = forms.ModelMultipleChoiceField(
        queryset=Period.objects.all(), label="Periodo", widget=djgentelella.SelectMultiple,
        required=False
    )
    currency = forms.MultipleChoiceField(
        choices=Group.COURRENCY_CHOICES, widget=djgentelella.SelectMultiple, label="Moneda",
        required=False
    )
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), widget=djgentelella.SelectMultiple, label="Categoría",
        required=False
    )
    open = forms.ChoiceField(
        choices=OPTIONS, widget=djgentelella.Select, label="Abierto", required=False,
    )


class GroupCreateForm(forms.ModelForm, GTForm):
    schedule = forms.CharField(
        required=False, max_length=250, widget=djgentelella.TextInput)

    class Meta:
        model = Group
        fields = [
            'name', 'period', 'course', 'schedule', 'pre_enroll_start',
            'pre_enroll_finish', 'enroll_start', 'enroll_finish', 'is_paid',
            'currency', 'cost', 'maximum', 'flow'
        ]
        widgets = {
            'name': djgentelella.TextInput,
            'period': djgentelella.Select,
            'course': djgentelella.Select,
            'pre_enroll_start': djgentelella.DateTimeInput,
            'pre_enroll_finish': djgentelella.DateTimeInput,
            'enroll_start': djgentelella.DateTimeInput,
            'enroll_finish': djgentelella.DateTimeInput,
            'is_paid': djgentelella.YesNoInput(
                attrs={'rel': ['currency', 'cost']}),
            'currency': djgentelella.Select,
            'cost': djgentelella.NumberInput,
            'maximum': djgentelella.NumberInput,
            'flow': djgentelella.Select

        }

    def __init__(self, *args, **kwargs):
        super(GroupCreateForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'period_id' in kwargs['initial']:
                self.fields['period'].initial = kwargs['initial']['period_id']
            if 'course_id' in kwargs['initial']:
                self.fields['course'].initial = kwargs['initial']['course_id']


class EnrollSearchForm(GTForm, forms.Form):
    student = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(), label="Estudiante",
        widget=djgentelella.SelectMultiple, required=False
    )
    group = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), widget=djgentelella.SelectMultiple,
        label="Grupo", required=False
    )


class EnrollCreateForm(forms.ModelForm, GTForm):
    class Meta:
        model = Enroll
        fields = [
            'student', 'group', 'enroll_finished', 'enroll_activate',
        ]
        widgets = {
            'student': djgentelella.Select,
            'group': djgentelella.Select,
            'enroll_finished': djgentelella.YesNoInput,
            'enroll_activate': djgentelella.YesNoInput,
        }

    def __init__(self, *args, **kwargs):
        super(EnrollCreateForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'group_id' in kwargs['initial']:
                self.fields['group'].initial = kwargs['initial']['group_id']
            if 'student_id' in kwargs['initial']:
                self.fields['student'].initial = kwargs['initial']['student_id']


class StudentSearchForm(GTForm, forms.Form):
    student = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        label="Nombre estudiate", widget=djgentelella.SelectMultiple,
        required=False
    )


class StudentAdminCreateForm(forms.ModelForm, GTForm):
    username = forms.CharField(
        label="Nombre de usuario", widget=djgentelella.TextInput, required=True
    )
    first_name = forms.CharField(
        label="Nombres", widget=djgentelella.TextInput, required=True)
    last_name = forms.CharField(
        label="Apellidos", widget=djgentelella.TextInput, required=True)
    email = forms.CharField(
        label="Correo", widget=djgentelella.EmailMaskInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class PageSearchForm(GTForm, forms.Form):
    slug = forms.CharField(
        label="Nombre", widget=djgentelella.TextInput, required=False)


class PageCreateForm(forms.ModelForm, GTForm):
    create_menu = forms.BooleanField(
        required=False, widget=djgentelella.YesNoInput(
            attrs={'rel': ['#create_menu_form']}, shparent='.x_panel'),
        label="¿Agregar página al menú?")
    content = forms.CharField(
        required=False, widget=widget.TextareaWysiwyg, label="Contenido")

    class Meta:
        model = Page
        fields = '__all__'
        widgets = {
            'slug': djgentelella.TextInput,
            'title': djgentelella.TextInput,
        }

    def __init__(self, *args, **kwargs):
        edit_page = kwargs.pop('edit_page', False)
        super(PageCreateForm, self).__init__(*args, **kwargs)
        if edit_page:
            del self.fields['create_menu']


class MenuItemAddForm(forms.ModelForm, GTForm):
    description = forms.CharField(required=False, widget=djgentelella.Textarea)
    order = forms.IntegerField(required=False, widget=djgentelella.NumberInput)

    class Meta:
        model = MenuItem
        fields = [
            'description', 'require_authentication', 'order',
            'parent', 'publicated', 'is_index'
        ]
        widgets = {
            'require_authentication': djgentelella.YesNoInput,
            'parent': djgentelella.Select,
            'publicated': djgentelella.YesNoInput,
            'is_index': djgentelella.YesNoInput
        }


class PreEnrollAddGroupForm(GTForm, forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=Enroll.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Matrícula")
    action = forms.CharField(required=True)
