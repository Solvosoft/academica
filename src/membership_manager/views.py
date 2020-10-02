from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q
from django.forms import modelformset_factory
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import ListView
from djgentelella.cruds.base import CRUDView
from djgentelella.forms.forms import GTBaseModelFormSet

from async_notifications.models import NewsLetterTemplate, EmailTemplate, EmailNotification
from async_notifications.tasks import send_email
from membership_core.models import Country, ServiceType, MembershipTemplate
from membership_core.models import ServiceMT
from membership_manager.dashboard import TopStats
from membership_manager.forms import MembershipServiceForm, ContactSearchForm, MembershipForm, ContactAddForm,\
    OrganizationSearchForm, OrganizationAddForm
from membership_manager.models import Contact, Organization, Membership, Service
from membership_manager.newsletterform import FilterEmailsForm, NewsLetterForm, NewsLetterTemplateForm, \
    EmailTemplateForm, EmailNotificationForm
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


class OrganizationListView(ListView):
    template_name = "organization/organization_list.html"
    paginate_by = 30

    def get_queryset(self):
        self.form = OrganizationSearchForm(self.request.GET)
        self.form.is_valid()
        queryset = Organization.objects.all()
        if self.form.cleaned_data['organization']:
            queryset = queryset.filter(
                Q(pk__in=self.form.cleaned_data['organization']))
        if self.form.cleaned_data['countries']:
            queryset = queryset.filter(
                Q(country__pk__in=self.form.cleaned_data['countries']))
        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['formsearch'] = OrganizationSearchForm(self.request.GET)
        return context


@permission_required('membership_manager.add_organization')
def create_organization(request):

    # We create a new organization
    if request.method == 'POST':

        # create a new organization object
        form = OrganizationAddForm(request.POST)

        # We save the form
        if form.is_valid():
            form.save()
            messages.success(request, "Organización guardada con exíto")
            return redirect('organizations')

        # if there are errors we return the error messages
        else:
            messages.error(
                request,
                "Error al intentar guardar la organización")

    # We display new contact form
    if request.method == 'GET':

        form = OrganizationAddForm()

    context = {
        'form': form
    }
    return render(request, 'organization/create.html', context=context)


@permission_required('membership_manager.change_organization')
def edit_organization(request, pk=None):

    # We create a new contact
    if request.method == 'POST':
        if pk is not None:
            # create a new organization object
            organization = Organization.objects.get(pk=pk)
            form = OrganizationAddForm(request.POST, instance=organization)

            # We save the form
            if form.is_valid():
                form.save()
                messages.success(request, "Organización guardada con exíto")
                return redirect('organizations')

            # if there are errors we return the error messages
            else:
                messages.error(
                    request,
                    "Error al intentar guardar la organiación")

    # We display new organization form
    if request.method == 'GET':
        if pk is not None:
            organization = Organization.objects.get(pk=pk)
            form = OrganizationAddForm(initial=organization.__dict__)

    context = {
        'form': form
    }
    return render(request, 'organization/edit.html', context=context)


@permission_required('membership_manager.delete_organization')
def delete_organization(request, pk):
    organization = Organization.objects.filter(pk=pk).first()
    if organization:
        organization.delete()
        messages.success(request, "Organización eliminada con exíto")
        return redirect('organizations')


class MembershipListView(ListView):
    template_name = "membership/membership_list.html"
    paginate_by = 30
    success_url = reverse_lazy('memberships')
    model = Membership

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = FilterEmailsForm(self.request.GET)
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
        context['form_filters'] = FilterEmailsForm(self.request.GET)
        context['form_template_newsletter'] = NewsLetterTemplateForm()
        context['form_template_email'] = EmailTemplateForm()
        context['mem_template'] = MembershipTemplate.objects.filter(state="active")
        return context


@permission_required('membership_manager.change_membership')
def edit_membership(request, pk=None):
    formset = modelformset_factory(
        Service, form=MembershipServiceForm, formset=GTBaseModelFormSet,
        can_delete=True, extra=1, can_order=True)

    # We will save or update
    if request.method == 'POST':
        # If there is a pk we will update
        if pk is not None:
            instance = Membership.objects.get(pk=pk)
            form = MembershipForm(request.POST, instance=instance)
            fset = formset(request.POST, queryset=Service.objects.filter(
                membership__pk=pk), prefix="mts")

            # We save or update the form and the formset
            if form.is_valid() and fset.is_valid():
                instm = form.save()
                instances = fset.save(commit=False)
                for delinst in fset.deleted_objects:
                    delinst.delete()
                for instance in instances:
                    instance.membership = instm
                    instance.save()
                messages.success(request, "Membresía guardada con exíto")
                return redirect('memberships')

        # if there are errors we return the error messages
        else:
            messages.error(
                request,
                "Error al intentar guardar los servicios asociados")

    # We will list data or show new form
    if request.method == 'GET':

        # if pk we need list related data
        if pk is not None:
            memberhsip = Membership.objects.get(pk=pk)
            extra = memberhsip.service_set.all().count()
            if extra == 0:
                extra = 1
            else:
                extra = 0
            formset = modelformset_factory(
                Service, form=MembershipServiceForm, formset=GTBaseModelFormSet,
                can_delete=True, extra=extra, can_order=True)
            form = MembershipForm(initial=memberhsip.__dict__)
            fset = formset(queryset=Service.objects.filter(membership__pk=pk), prefix='mts')
            context = {
                'form': form,
                'formset': fset
            }
            return render(request, 'membership/edit.html', context=context)

        else:
            messages.error("No fue posible cargar la membresía")
    return redirect("memberships")


@permission_required('membership_manager.add_membership')
def create_membership(request):
    m_template = {}
    t = request.GET.get('t', None)
    formset = modelformset_factory(
        Service, form=MembershipServiceForm, formset=GTBaseModelFormSet,
        can_delete=True, extra=1, can_order=True)

    # We will save or update
    if request.method == 'POST':

        # create a new object membership
        form = MembershipForm(request.POST)
        fset = formset(
            request.POST, queryset=Service.objects.none(), prefix="mts")

        # We save the form and the formset
        if form.is_valid() and fset.is_valid():
            instm = form.save()
            instances = fset.save(commit=False)
            for instance in instances:
                instance.membership = instm
                instance.save()
            messages.success(request, "Membresía guardada con exíto")
            return redirect('memberships')

        # if there are errors we return the error messages
        else:
            messages.error(
                request,
                "Error al intentar guardar los servicios asociados")

    # We will list data or show new form
    if request.method == 'GET':

        # if there is a template load initial data
        if t is not None and t != "":
            m_template = MembershipTemplate.objects.get(pk=t).__dict__
            form = MembershipForm(initial=m_template)
            servicesmt = ServiceMT.objects.filter(membership__pk=t)
            templateinitial = []
            for services in servicesmt:
                for service in servicesmt:
                    templateinitial.append({
                        'servicetype': service.servicetype,
                        'description': service.description,
                        'observations': service.observations
                    })
            extra = servicesmt.count()
            if servicesmt.count() == 0:
                extra = 1
            formset = modelformset_factory(
                Service, form=MembershipServiceForm,
                formset=GTBaseModelFormSet,
                can_delete=True, extra=extra)
            fset = formset(
                queryset=Service.objects.none(), initial=templateinitial,
                prefix='mts')

        # load the data without initial information
        else:
            form = MembershipForm()
            fset = formset(queryset=Service.objects.none(), prefix='mts')
    context = {
        'form': form,
        'formset': fset
    }
    return render(request, 'membership/create.html', context=context)


@permission_required('membership_manager.delete_membership')
def delete_memberships(request, pk):
    membership = Membership.objects.filter(pk=pk).first()
    if membership:
        membership.delete()
        messages.success(request, "Membresía eliminada con exíto")
        return redirect('memberships')


class ContactListView(ListView):
    template_name = "contact/contact_list.html"
    paginate_by = 30

    def get_queryset(self):
        self.form = ContactSearchForm(self.request.GET, initial={'apply_filters': True})
        self.form.is_valid()
        queryset = Contact.objects.all()
        if self.form.cleaned_data['contact']:
            queryset = queryset.filter(
                Q(pk__in=self.form.cleaned_data['contact']))
        if self.form.cleaned_data['countries']:
            queryset = queryset.filter(
                Q(country__pk__in=self.form.cleaned_data['countries']))
        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['formsearch'] = ContactSearchForm(self.request.GET)
        return context


@permission_required('membership_manager.add_contact')
def create_contacts(request):

    # We create a new contact
    if request.method == 'POST':

        # create a new contact object
        form = ContactAddForm(request.POST)

        # We save the form and the formset
        if form.is_valid():
            form.save()
            messages.success(request, "Contacto guardado con exíto")
            return redirect('contacts')

        # if there are errors we return the error messages
        else:
            messages.error(
                request,
                "Error al intentar guardar el contacto")

    # We display new contact form
    if request.method == 'GET':
        form = ContactAddForm()

    context = {
        'form': form
    }
    return render(request, 'contact/create.html', context=context)


@permission_required('membership_manager.change_contact')
def edit_contacts(request, pk=None):

    # We will update
    if request.method == 'POST':
        # If there is a pk we will update
        if pk is not None:
            instance = Contact.objects.get(pk=pk)
            form = ContactAddForm(request.POST, instance=instance)

            # We update the form and the formset
            if form.is_valid():
                form.save()
                messages.success(request, "Contacto guardado con exíto")
                return redirect('contacts')
            # if there are errors we return the error messages
            else:
                messages.error(
                    request,
                    "Error al actualizar el contacto")

    # We display a new form
    if request.method == 'GET':
        contact = Contact.objects.get(pk=pk)
        form = ContactAddForm(initial=contact.__dict__)
    context = {
        'form': form,
    }
    return render(request, 'contact/edit.html', context=context)


@permission_required('membership_manager.delete_contact')
def delete_contacts(request, pk):
    contact = Contact.objects.filter(pk=pk)
    if contact:
        contact.delete()
        messages.success(request, "Contacto eliminado con exíto")
        return redirect('contacts')


@permission_required('async_notifications.delete_newsletter')
def delete_membership_service(request, pk):
    boletin = NewsLetter.objects.filter(pk=pk).first()
    if boletin:
        boletin.delete()
        return redirect('news_letter_list')


@permission_required('async_notifications.add_newsletter')
def create_news_letter_membership(request):

    templateform = NewsLetterTemplateForm(request.GET)
    templateform.is_valid()
    template = get_object_or_404(NewsLetterTemplate, pk=templateform.cleaned_data['news_letter_template'].pk)
    form_filter = FilterEmailsForm(request.GET)
    form_filter.is_valid()
    form = NewsLetterForm(initial={'message': template.message})

    return render(request, "news_letter/create_news_letter.html", context={'form': form,
                                                                           'template': template.pk,
                                                                           'form_filter': form_filter})


def email_template(request, pk):

    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)

        if form.is_valid():
            template = form.cleaned_data['email_template']

            if template:
                return redirect('create_email_notification', pk=template.pk, membership=pk)
            else:
                return redirect('create_email_notification', pk=0, membership=pk)


@permission_required('async_notifications.add_emailnotification')
def create_email_notification(request, pk, membership):

    membresia = get_object_or_404(Membership, pk=membership)
    emails = []

    if request.method == "POST":

        form = EmailNotificationForm(request.POST)

        if form.is_valid():
            emailnotification = EmailNotification(
                subject = form.cleaned_data['subject'],
                message = form.cleaned_data['message'],
                bcc = str(", ".join(form.cleaned_data['bcc'].values_list('email', flat=True))),
                cc = str(", ".join(form.cleaned_data['cc'].values_list('email', flat=True))),
                user = request.user,
                recipient = form.cleaned_data['recipient'],
                file = form.cleaned_data['file']
            )
            emailnotification.save()
            obj = EmailNotification.objects.all().last()
            send_email(obj.pk)
            messages.success(request, 'Notificación de correo electrónico generada exitosamente.')
            return redirect('memberships')
    else:

        if membresia.organization:
            emails.append(membresia.organization.email)
        if membresia.contact:
            emails.append(membresia.contact.email)

        if pk == 0:
            form = EmailNotificationForm(initial={'recipient': ", ".join(emails)})
        else:
            template = get_object_or_404(EmailTemplate, pk=pk)
            form = EmailNotificationForm(initial={'subject':template.subject,
                                                  'message': template.message,
                                                  'recipient': ", ".join(emails)})

    return render(request, "membership/create_email_notification.html", context={'form': form,
                                                                                 'template': pk})