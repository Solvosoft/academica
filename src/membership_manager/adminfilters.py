from ajax_select.fields import AutoCompleteSelectMultipleField
from django import forms
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from membership_manager.models import Organization, Membership
from django_countries import countries


class PaisFilter(admin.SimpleListFilter):
    title = 'Países'
    parameter_name = 'pais'

    def get_country(self, code, name):
        return "%d | %d | %d | %s "%(
        Membership.objects.filter(
            organization__country=code
        ).count(),
        Membership.objects.filter(
            Q(state='active') | Q(state='graceperiod'),
            organization__country=code ).count(),
        Membership.objects.filter(
            organization__country=code,
            state='inactive'
        ).count(), name
        )
    def lookups(self, request, model_admin):
        keys = set(Organization.objects.all().values_list('country', flat=True))
        country=dict(countries)
        options = [('all', 'T | A | I | Nombre')]+[(x, self.get_country(x, country[x])) for x in keys]
        return options

    def queryset(self, request, queryset):
        print(queryset)
        value = self.value()
        if value and value != 'all':
            return queryset.filter( country=value)
        return queryset



class FormFilter(admin.ListFilter):
    template = 'admin/admin_form_filter.html'
    field = None
    form_class = None
    mapped_keys = None
    hidden_parameters = None

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)
        if self.form_class is None:
            raise ImproperlyConfigured(
                "The list filter '%s' does not specify a 'form_class'."
                % self.form_class.__name__
            )

        self.request = request
        self.form = self.form_class(request.GET)
        self.form.is_valid()
        for parameter_name in self.form.fields.keys():
            if parameter_name in params:
                value = params.pop(parameter_name)
                self.used_parameters[parameter_name] = value

        for parameter_name in self.get_hidden_parameters():
            if parameter_name in params:
                params.pop(parameter_name)



    def get_form(self):
        return self.form

    def has_output(self):
        return True

    def lookups(self, request, model_admin):
        return None

    def get_map_keys(self, name):
        if self.mapped_keys is not None:
            if name in self.mapped_keys:
                return self.mapped_keys[name]
        return [name]

    def get_hidden_parameters(self):
        dev = []
        if self.hidden_parameters is not None:
            dev = self.hidden_parameters
        return dev

    def expected_parameters(self):
        return self._expected_parameters() + self.get_hidden_parameters()

    def _expected_parameters(self):
        return list(self.form.fields.keys())

    def value(self):
        """
        Return the value (in string format) provided in the request's
        query string for this filter, if any, or None if the value wasn't
        provided.
        """
        data = {}
        for parameter_name in self.form.fields.keys():
            for name in self.get_map_keys(parameter_name):
                val = self.form.cleaned_data.get(
                    parameter_name,
                    self.used_parameters.get(parameter_name))

                if val is not None:
                    data[name] = val
        if data:
            return data

    def choices(self, changelist):

        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=self.expected_parameters()),
            'display': _('All'),
        }

    def get_queryset_parameters(self, data):
        return data

    def queryset(self, request, queryset):
        term = self.value()

        if term is None:
            return
        term = self.get_queryset_parameters(term)
        return queryset.filter(**term)

class OrgForm(forms.Form):
    org = AutoCompleteSelectMultipleField('orgs', required=False)
    cont = AutoCompleteSelectMultipleField('contacts', required=False)
    pais = forms.ChoiceField(choices=(), required=False )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        keys = set(Organization.objects.all().values_list('country', flat=True))
        country=dict(countries)

        self.fields['pais'].choices =  [('', '---------')]+[(x,country[x]) for x in keys]


class OrganizationFilter(FormFilter):
    title = 'Organizaciones'
    parameter_name = 'org'
    field = 'organization__name__icontains'
    form_class = OrgForm
    hidden_parameters = ['cont_text', 'org_text', 'submit']
    mapped_keys = {'org': ['organization_id__in'],
                   'cont': ['contact_id__in'],
                   'pais': ['organization__country']}

    def get_queryset_parameters(self,term):
        delitem = []
        for k in term:
            if not term[k] :
                delitem.append(k)

        for k in delitem:
            del term[k]
        return term