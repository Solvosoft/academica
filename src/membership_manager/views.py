import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models import Q
from django.views.generic import ListView
from djgentelella.cruds.base import CRUDView
from membership_core.models import Country, ServiceType, SystemCurrency, \
    MembershipTemplate
from membership_manager.dashboard import TopStats
from membership_manager.models import Contact, Organization, Membership
from membership_manager.forms import MembershipForm
from membership_manager.newsletterform import FilterEmailsForm


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

    def get_queryset(self):

        filters = {}

        queryset = Membership.objects.all()
        q = self.request.GET.get('q', None)
        p = self.request.GET.get('p', None)
        s = self.request.GET.get('s', None)
        c = self.request.GET.get('c', None)
        d = self.request.GET.get('d', None)
        if q is not None and q != '':
            # need to implement other filters
            queryset = queryset.annotate(fullname_organization=Concat(
                'organization__contact__first_name',
                Value(' '), 'organization__contact__last_name'))
            queryset = queryset.annotate(fullname_contact=Concat(
                'contact__first_name',
                Value(' '), 'contact__last_name'))
            queryset = queryset.filter(
                Q(organization__name__icontains=q) |
                Q(fullname_organization__icontains=q) |
                Q(fullname_contact__icontains=q)
            )

        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['p'] = self.request.GET.get('p', '')
        context['s'] = self.request.GET.get('s', '')
        context['c'] = self.request.GET.get('c', '')
        context['d'] = self.request.GET.get('d', '')
        context['today'] = datetime.datetime.now
        context['form_filters'] = FilterEmailsForm(initial={'apply_filters': True})
        context['mem_template'] = MembershipTemplate.objects.filter(
            state="active")
        return context


@login_required
def create_membership(request):
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membresía agregada con exíto.')
    if request.method == 'GET':
        m_template = {}
        t = request.GET.get('t', None)
        if t is not None and t != "":
            m_template = MembershipTemplate.objects.get(pk=t)
    context = {
        'form': MembershipForm(),
        't': m_template
    }
    return render(request, 'membership/create.html', context=context)


class ContactListView(ListView):
    template_name = "contact/contact_list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Contact.objects.all()
        q = self.request.GET.get('q')
        if(q is not None):
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
