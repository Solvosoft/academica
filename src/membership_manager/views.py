import datetime
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse
from django.contrib import messages
from django.db.models.functions import Concat
from django.db.models import Value
from django.db.models import Q
from django.views.generic import ListView
from djgentelella.cruds.base import CRUDView
from membership_core.models import Country, ServiceType, SystemCurrency, \
    MembershipTemplate
from membership_manager.dashboard import TopStats
from membership_manager.models import Contact, Organization, Membership,\
    Service
from membership_manager.forms import MembershipForm, MembershipServicesForm


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
    paginate_by = 10

    def get_queryset(self):
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
        if p is not None and p != "":
            queryset = queryset.filter(
                Q(organization__country__pk=p))
        if s is not None and s != "":
            queryset = queryset.filter(
                Q(state__exact=s)
            )
        if c is not None and c != "":
            queryset = queryset.filter(
                Q(currency__currency__exact=c)
            )
        if d is not None and d != "":
            if d == "yes":
                queryset = queryset.filter(
                    mem_inv__renewal_period__encobro=True,
                    mem_inv__renewal_period__active=True,
                    # pending to implement by date
                    # mem_inv__renewal_period__start_date__lte=datetime.datetime.now
                )
            elif d == "no":
                queryset = queryset.exclude(
                    mem_inv__renewal_period__encobro=True,
                    mem_inv__renewal_period__active=True,
                    # pending to implement by date
                    # mem_inv__renewal_period__start_date__lte=datetime.datetime.now
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
        context['currency'] = SystemCurrency.objects.all()
        context['states'] = Membership.STATES
        context['countries'] = Country.objects.all()
        context['mem_template'] = MembershipTemplate.objects.filter(
            state="active")
        return context


@login_required
def create_membership(request):
    m_template = {}
    t = request.GET.get('t', None)
    if request.method == 'POST':
        form = MembershipForm(request.POST)
        if form.is_valid():
            inst = form.save()
            messages.success(request, 'Membresía guardada con exíto!')
            return redirect('add_membership_services', pk=inst.pk)
        else:
            messages.warning(request, "Faltan datos por ingresar")
    if request.method == 'GET':
        if t is not None and t != "":
            m_template = MembershipTemplate.objects.get(pk=t)
            form = MembershipForm()
    context = {
        'form': form,
        't': m_template
    }
    return render(request, 'membership/create.html', context=context)


@login_required
def add_services(request, pk):
    form = MembershipServicesForm()
    if request.POST:
        form = form = MembershipServicesForm(request.POST)
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


@permission_required('async_notifications.delete_newsletter')
def delete_membership_service(request, pk):
    boletin = NewsLetter.objects.filter(pk=pk).first()

    if boletin:
        boletin.delete()
        return redirect('news_letter_list')