# encoding: utf-8

'''
Created on 7/4/2015

@author: luisza
'''
from django import forms
from matricula.models import Student, Page, MenuItem, Category, Course,\
    Period, Group, Enroll, Professor
from django.utils.translation import ugettext_lazy as _
from django.core import validators
from django.contrib.auth.models import User
from djgentelella.widgets import core as djgentelella
from djgentelella.forms.forms import GTForm
from djgentelella.widgets.selects import AutocompleteSelect
from djgentelella.models import MenuItem as DJMenuItem
from django.contrib.auth.models import Permission
from djgentelella.widgets.selects import AutocompleteSelectMultiple
from djgentelella.widgets import tinymce
from matricula.views.utils import get_active_period


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
        label=_('First name'), max_length=30, required=True,
        widget=djgentelella.TextInput)
    last_name = forms.CharField(
        label=_('Last name'), max_length=30, required=True,
        widget=djgentelella.TextInput)
    email = forms.EmailField(required=True, widget=djgentelella.EmailMaskInput)
    password = forms.CharField(
        required=True, label=_("Password"), widget=djgentelella.PasswordInput)
    password_check = forms.CharField(
        widget=djgentelella.PasswordInput, required=True,
        label=_("Repeat password"))
    organization = forms.CharField(
        label="Organización", required=True
    )

    class Meta:
        model = Student
        fields = [
            'name', 'first_name', 'last_name', 'email',
            'password', 'password_check', 'organization']
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

    def __init__(self, *args, **kwargs):
        super(MenuItemFormPage, self).__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['name'] = forms.ModelChoiceField(
                queryset=Page.objects.all(), label=_("Page"),
                initial=kwargs['instance'].name)


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
        label='Término', required=False,
        widget=djgentelella.TextInput)


class CourseSearchForm(GTForm, forms.Form):
    name = forms.CharField(
        label='Término', required=False,
        widget=djgentelella.TextInput)
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Categoría")


class CourseCreateForm(forms.ModelForm, GTForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'name': djgentelella.TextInput,
            'content': tinymce.EditorTinymce,
            'category': AutocompleteSelect('categorybasename'),
        }

    def __init__(self, *args, **kwargs):
        super(CourseCreateForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            if 'category_id' in kwargs['initial']:
                self.fields['category'].initial = kwargs['initial']['category_id']


class GroupAddForm(forms.ModelForm, GTForm):
    schedule = forms.CharField(
        required=False, max_length=250, widget=djgentelella.TextInput,
        label=_("Schedule"))

    class Meta:
        model = Group
        fields = [
            'name', 'period', 'schedule', 'pre_enroll_start', 'pre_enroll_finish',
            'enroll_start', 'enroll_finish', 'is_paid', 'currency', 'cost',
            'maximum', 'is_open', 'flow'
        ]
        widgets = {
            "name": djgentelella.TextInput,
            "schedule": djgentelella.TextInput,
            "pre_enroll_start": djgentelella.DateTimeInput,
            "pre_enroll_finish": djgentelella.DateTimeInput,
            'period': AutocompleteSelect('periodbasename'),
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['period'].required = True


class MenuItemSearchForm(GTForm, forms.Form):
    title = forms.CharField(
        required=False, widget=djgentelella.TextInput,
        label="Título")
    parent = forms.ModelMultipleChoiceField(
        queryset=DJMenuItem.objects.all(), required=False,
        widget=djgentelella.SelectMultiple, label="Padre"
    )


class MenuItemCreateForm(forms.ModelForm, GTForm):
    class Meta:
        model = DJMenuItem
        fields = [
            'title', 'url_name', 'category', 'is_reversed',
            'reversed_kwargs', 'reversed_args', 'parent',
            'is_widget', 'icon', 'only_icon']
        widgets = {
            'title': djgentelella.TextInput,
            'url_name': djgentelella.TextInput,
            'category': djgentelella.TextInput,
            'is_reversed': djgentelella.YesNoInput,
            'reversed_kwargs': djgentelella.TextInput,
            'reversed_args': djgentelella.TextInput,
            'parent': djgentelella.Select,
            'is_widget': djgentelella.YesNoInput,
            'icon': djgentelella.TextInput,
            'only_icon': djgentelella.YesNoInput
        }
        labels = {
            'title': _('Title'),
            'url_name': _('Url name'),
            'category': _('Category'),
            'is_reversed': _('Is reversed?'),
            'reversed_kwargs': _('Reversed kwargs'),
            'reversed_args': _('Reversed args'),
            'parent': _('Parent'),
            'is_widget': _('Is a widget?'),
            'icon': _('Icon'),
            'only_icon': _('Only icon?')
        }

    def __init__(self, *args, **kwargs):
        super(MenuItemCreateForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            print(kwargs)
            if 'permission_id' in kwargs['initial']:
                self.fields['permission'].initial = kwargs['initial']['permission_id']


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
    name = forms.CharField(
        required=False, widget=djgentelella.TextInput,
        label="Nombre")
    course = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(), widget=djgentelella.SelectMultiple,
        label="Curso", required=False
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
        required=False, max_length=250, widget=djgentelella.TextInput,
        label=_("Schedule"))

    class Meta:
        model = Group
        fields = [
            'name', 'course', 'period', 'schedule', 'pre_enroll_start',
            'pre_enroll_finish', 'enroll_start', 'enroll_finish', 'is_paid', 'currency',
            'cost', 'maximum', 'flow', 'professors'
        ]
        widgets = {
            'name': djgentelella.TextInput,
            'course': djgentelella.Select,
            'period': AutocompleteSelect('periodbasename'),
            'pre_enroll_start': djgentelella.DateTimeInput,
            'pre_enroll_finish': djgentelella.DateTimeInput,
            'enroll_start': djgentelella.DateTimeInput,
            'enroll_finish': djgentelella.DateTimeInput,
            'is_paid': djgentelella.YesNoInput(
                attrs={'rel': ['currency', 'cost']}),
            'currency': djgentelella.Select,
            'cost': djgentelella.NumberInput,
            'maximum': djgentelella.NumberInput,
            'flow': djgentelella.Select,
            'professors': djgentelella.SelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super(GroupCreateForm, self).__init__(*args, **kwargs)

        self.fields['professors'].queryset = Professor.objects.filter(active=True)

        if 'initial' in kwargs:
            if 'course_id' in kwargs['initial']:
                self.fields['course'].initial = kwargs['initial']['course_id']


class GroupEditForm(forms.ModelForm, GTForm):
    schedule = forms.CharField(
        required=False, max_length=250, widget=djgentelella.TextInput,
        label=_("Schedule"))

    class Meta:
        model = Group
        fields = [
            'name', 'course', 'period', 'schedule', 'pre_enroll_start',
            'pre_enroll_finish', 'enroll_start', 'enroll_finish', 'is_paid',
            'currency', 'cost', 'maximum', 'flow', 'professors'
        ]
        widgets = {
            'name': djgentelella.TextInput,
            'course': djgentelella.Select,
            'period': djgentelella.Select,
            'pre_enroll_start': djgentelella.DateTimeInput,
            'pre_enroll_finish': djgentelella.DateTimeInput,
            'enroll_start': djgentelella.DateTimeInput,
            'enroll_finish': djgentelella.DateTimeInput,
            'is_paid': djgentelella.YesNoInput(
                attrs={'rel': ['currency', 'cost']}),
            'currency': djgentelella.Select,
            'cost': djgentelella.NumberInput,
            'maximum': djgentelella.NumberInput,
            'flow': djgentelella.Select,
            'professors': djgentelella.SelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super(GroupEditForm, self).__init__(*args, **kwargs)
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
    IS_ACTIVE = (
        (None, "Todos"),
        (True, "Sí"),
        (False, "No")
    )
    student = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(),
        label="Nombre", widget=djgentelella.SelectMultiple,
        required=False)
    group = forms.ModelChoiceField(
        label="Grupo", widget=djgentelella.Select, required=False,
        queryset=Group.objects.all())
    organization = forms.CharField(
        label="Organización", widget=djgentelella.TextInput, required=False)
    active = forms.ChoiceField(
        choices=IS_ACTIVE, widget=djgentelella.Select,
        required=False, label="Activo")


class StudentAdminCreateForm(GTForm, forms.ModelForm):
    username = forms.CharField(
        label="Nombre de usuario", widget=djgentelella.TextInput, required=True
    )
    first_name = forms.CharField(
        label="Nombres", widget=djgentelella.TextInput, required=True)
    last_name = forms.CharField(
        label="Apellidos", widget=djgentelella.TextInput, required=True)
    email = forms.CharField(
        label="Correo", widget=djgentelella.EmailMaskInput, required=True)
    organization = forms.CharField(
        label="Organización", required=True
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'organization']


class PageSearchForm(GTForm, forms.Form):
    slug = forms.CharField(
        label="Nombre", widget=djgentelella.TextInput, required=False)


class PageCreateForm(forms.ModelForm, GTForm):
    create_menu = forms.BooleanField(
        required=False, widget=djgentelella.YesNoInput(
            attrs={'rel': ['#create_menu_form']}, shparent='.x_panel'),
        label="¿Agregar página al menú?")
    title = forms.CharField(
        label="Título", required=True, widget=djgentelella.TextInput)
    content = forms.CharField(
        required=False, widget=tinymce.EditorTinymce, label="Contenido")

    class Meta:
        model = Page
        fields = '__all__'
        widgets = {
            'slug': djgentelella.TextInput,
        }

    def __init__(self, *args, **kwargs):
        edit_page = kwargs.pop('edit_page', False)
        super(PageCreateForm, self).__init__(*args, **kwargs)
        if edit_page:
            del self.fields['create_menu']


class MenuItemAddForm(forms.ModelForm, GTForm):
    parent = forms.ModelChoiceField(
        queryset=DJMenuItem.objects.all(), label="Menú padre",
        required=False, widget=djgentelella.Select)
    permission = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(), label="Permisos requeridos",
        widget=djgentelella.SelectMultiple, required=False)

    class Meta:
        model = DJMenuItem
        fields = '__all__'
        fields = ['parent', 'permission']


class PreEnrollAddGroupForm(GTForm, forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=Enroll.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Matrícula")
    action = forms.CharField(required=True)


class QualifyStudentForm(GTForm, forms.ModelForm):
    class Meta:
        model = Enroll
        fields = ['course_status']
        widgets = {
            'course_status': djgentelella.Select
        }


class ProfessorEditForm(GTForm, forms.Form):
    username = forms.CharField(label="Nombre de usuaria", widget=djgentelella.TextInput, required=False)
    first_name = forms.CharField(label="Nombre", widget=djgentelella.TextInput, required=True)
    last_name = forms.CharField(label="Apellidos", widget=djgentelella.TextInput, required=True)
    email = forms.CharField(label="Correo electrónico como usuaria del sistema", widget=djgentelella.EmailMaskInput,
                            required=True)
    email_students = forms.CharField(label="Correo electrónico para estudiantes", widget=djgentelella.EmailMaskInput,
                                     required=True)
    description = forms.CharField(widget=djgentelella.Textarea, required=True, label="Descripción",
                                  help_text="Esta descripción será mostrada en los grupos en los cuales sea asignada como profesora.")


class ProfessorSearchForm(GTForm, forms.Form):
    PROFESSOR_STATES = (
        (None, "Todas"),
        (True, "Activas"),
        (False, "Inactivas"),
    )

    professor = forms.ModelMultipleChoiceField(
        queryset=Professor.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Profesora")

    status = forms.ChoiceField(
        choices=PROFESSOR_STATES, widget=djgentelella.Select, required=False, label="Estado")


class ProfessorAddForm(GTForm, forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(), widget=djgentelella.Select,
        required=False, label="Usuaria")

    class Meta:
        model = Professor
        fields = "__all__"
        widgets = {
            'email': djgentelella.EmailMaskInput,
            'description': djgentelella.Textarea,
            'active': djgentelella.YesNoInput
        }


class CouponsSearchForm(GTForm, forms.Form):
    DISCOUNT_CHOICES = (
        (None, "Todos"),
        (50, "50"),
        (100, "100")
    )

    IS_USED_CHOICES = (
        (None, "Todos"),
        (True, "Sí"),
        (False, "No")
    )

    student = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Estudiante")

    course = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Curso")

    is_used = forms.ChoiceField(
        choices=IS_USED_CHOICES, widget=djgentelella.Select,
        required=False, label="Utilizado")

    discount_percentage = forms.ChoiceField(
        choices=DISCOUNT_CHOICES, widget=djgentelella.Select,
        required=False, label="Descuento")


class PermissionForm(GTForm, forms.Form):
    permission = forms.ModelMultipleChoiceField(
        widget=AutocompleteSelectMultiple('permission'),
        queryset=Permission.objects.all(),
        label="Permisos", required=False)


class CouponAddForm(GTForm, forms.Form):

    DISCOUNT_CHOICES = (
        (50, "50"),
        (100, "100")
    )

    student = forms.ModelMultipleChoiceField(
        queryset=Student.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Estudiante")

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), widget=djgentelella.Select,
        required=False, label="Curso")

    discount_percentage = forms.ChoiceField(
        choices=DISCOUNT_CHOICES, widget=djgentelella.Select,
        required=False, label="Descuento")


class CouponEditForm(GTForm, forms.Form):

    DISCOUNT_CHOICES = (
        (50, "50"),
        (100, "100")
    )

    student = forms.ModelChoiceField(
        queryset=Student.objects.all(), widget=djgentelella.Select,
        required=False, label="Estudiante")

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), widget=djgentelella.Select,
        required=False, label="Curso")

    discount_percentage = forms.ChoiceField(
        choices=DISCOUNT_CHOICES, widget=djgentelella.Select,
        required=False, label="Descuento")


class CourseMainSearchForm(GTForm, forms.Form):
    IS_PAID = (
        (0, "No filtrar"),
        (1, "Pagados"),
        (2, "Gratis")
    )
    name = forms.CharField(
        label='Término', required=False,
        widget=djgentelella.TextInput)
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Categoría")
    course = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(), widget=djgentelella.SelectMultiple,
        required=False, label="Cursos")
    is_paid = forms.ChoiceField(
        choices=IS_PAID, widget=djgentelella.Select,
        required=False, label="Pagado")
