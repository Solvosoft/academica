from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.db.models import Value
from django.db.models.functions import Concat
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.forms import modelformset_factory
from django.views.generic import ListView
from djgentelella.cruds.base import CRUDView
from membership_core.models import Country, ServiceType, MembershipTemplate
from membership_manager.dashboard import TopStats
from membership_manager.forms import MembershipForm, MembershipServiceForm
from membership_manager.newsletterform import FilterEmailsForm
from membership_manager.models import Contact, Organization, Membership,\
    Service
from djgentelella.forms.forms import GTBaseModelFormSet
from .news_letter import NewsLetter


def servicios_stats():
    for service in ServiceType.objects.all():
        yield (service.name, service.service_set.count())


def country_stats():
    for country in Country.objects.all().order_by('name'):
        total = Membership.objects.filter(
            Q(organization__country=country) | Q(contact__country=country),
            state='active'
        ).distinct().count()
        if total:
            yield (country.flag, country.name, total)


@login_required
def index(request):
    context = {'topstat': TopStats(),
               'vencimientoanual_url': reverse('vencimientoanual-list'),
               'pagoanual_url': reverse('pagoanual-list'),
               'countries': country_stats(),
               'servicios_stats': servicios_stats()
               }
    return render(request, 'membership/home.html', context=context)


class OrganizationView(CRUDView):
    model = Organization
    template_name_base = "membership/djgentelella/cruds"


class MembershipListView(ListView):
    template_name = "membership/membership_list.html"
    paginate_by = 30
    success_url = reverse_lazy('memberships')
    model = Membership

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = FilterEmailsForm(self.request.GET, initial={'apply_filters': True})
        self.form.is_valid()

        filters = {}
        if self.form.cleaned_data['name']:
            queryset = self.form.cleaned_data['name']
        if self.form.cleaned_data['state']:
            filters['state'] = self.form.cleaned_data['state']

        if self.form.cleaned_data['country']:
            queryset = queryset.filter(Q(organization__country__in=self.form.cleaned_data['country'])|Q(
                contact__country__in=self.form.cleaned_data['country']))

        if self.form.cleaned_data['currency']:
            filters['currency__in'] = self.form.cleaned_data['currency']

        if self.form.cleaned_data['payment_method']:
            filters['payment_method__in'] = self.form.cleaned_data['payment_method']

        if self.form.cleaned_data['membership_type']:
            filters['membership_type__in'] = self.form.cleaned_data['membership_type']

        if self.form.cleaned_data['service_type']:
            filters['service__servicetype__in'] = self.form.cleaned_data['service_type']

        if self.form.cleaned_data['invoices']:
            filters['mem_inv__status'] = self.form.cleaned_data['invoices']

        return queryset.filter(**filters)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['today'] = now()
        context['form_filters'] = self.form
        context['mem_template'] = MembershipTemplate.objects.filter(state="active")
        return context


@login_required
def create_membership(request):
    m_template = {}
    t = request.GET.get('t', None)
    formset = modelformset_factory(
        Service, form=MembershipServiceForm, formset=GTBaseModelFormSet,
        can_delete=True, extra=1)
    valid = True
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            inst = form.save()
            messages.success(request, 'Membresía guardada con exíto!')
            fset = formset(
                request.POST, queryset=None, prefix='ser')
        valid = fset.is_valid()
        if valid:
            fset.save(commit=False)
            for f in fset:
                f.instance.membership = inst
                f.save()
            messages.success(request, "Formset saved successfully")
            return redirect('memberships')
        else:
            messages.warning(request, "Faltan datos por ingresar")
    if request.method == 'GET':
        if t is not None and t != "":
            m_template = MembershipTemplate.objects.get(pk=t)
            form = MembershipForm()
            fset = formset(
                queryset=Service.objects.filter(membership__pk=t),
                prefix='ser')
    context = {
        'form': form,
        't': m_template,
        'formset': fset
    }
    return render(request, 'membership/create.html', context=context)


@login_required
def add_services(request, pk):
    form = MembershipServiceForm()
    if request.POST:
        form = form = MembershipServiceForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Servicio Guardado con exíto')
            form.save()
    services = Service.objects.filter(membership__pk=pk)
    context = {
        'pk': pk,
        'form': form,
        'services': services
    }
    return render(
        request, 'membership/membership_services.html', context=context)


class ContactListView(ListView):
    template_name = "contact/contact_list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Contact.objects.all()
        q = self.request.GET.get('q')
        if q is not None:
            queryset = queryset.annotate(fullname=Concat(
                'first_name', Value(' '), 'last_name'))
            queryset = queryset.filter(
                Q(email__icontains=q) | Q(fullname__icontains=q))
        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


@permission_required('async_notifications.delete_newsletter')
def delete_membership_service(request, pk):
    boletin = NewsLetter.objects.filter(pk=pk).first()
    if boletin:
        boletin.delete()
        return redirect('news_letter_list')
