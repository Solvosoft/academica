from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.forms import modelformset_factory
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView
from djgentelella.forms.forms import GTBaseModelFormSet

from membership_core.models import MembershipTemplate, ServiceMT
from membership_manager.forms import MembershipServiceForm, MembershipForm, MembershipTemplateForm
from membership_manager.models import Membership, Service, MembershipRenew
from membership_manager.newsletterform import FilterEmailsForm, NewsLetterTemplateForm, \
    EmailTemplateForm
from membership_manager.renew_utils import create_renew
from membership_manager.utils import add_logentry


@method_decorator(permission_required('membership_manager.view_membership'), name='dispatch')
class MembershipListView(ListView):
    template_name = "membership/membership_list.html"
    paginate_by = 30
    success_url = reverse_lazy('memberships')
    model = Membership

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(MembershipListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = FilterEmailsForm(self.request.GET)
        self.form.is_valid()

        filters = {}

        if self.form.cleaned_data['name']:
            filters['organization__in'] = self.form.cleaned_data['name']

        if self.form.cleaned_data['state']:
            filters['state'] = self.form.cleaned_data['state']

        if self.form.cleaned_data['country']:
            filters['organization__country__in'] = self.form.cleaned_data['country']

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

        context['today'] = timezone.now()
        context['form_filters'] = FilterEmailsForm(self.request.GET)
        context['form_template_newsletter'] = NewsLetterTemplateForm()
        context['form_template_email'] = EmailTemplateForm()
        context['mem_template'] = MembershipTemplateForm()
        return context


@method_decorator(permission_required('membership_manager.change_membership'), name='dispatch')
class EditMembership(UpdateView):
    model = Membership
    form_class = MembershipForm
    template_name = 'membership/edit.html'
    success_url = reverse_lazy('memberships')


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        contact = None
        organization = None
        contact_type = "organization"

        if self.object.organization.type:
            contact = self.object.organization
            contact_type = "contact"
        else:
            organization = self.object.organization

        kwargs['initial']={
            'contact': contact,
            'organization': organization,
            'contact_type': contact_type
        }
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        membership = context['object']

        extra = membership.service_set.all().count()
        if extra == 0:
            extra = 1
        else:
            extra = 0
        formset = modelformset_factory(
            Service, form=MembershipServiceForm, formset=GTBaseModelFormSet,
            can_delete=True, extra=extra, can_order=True)
        fset = formset(queryset=Service.objects.filter(membership=membership), prefix='mts')
        context['formset'] = fset
        context['contact_type'] = 'contact' if membership.organization.type else 'organization'
        context['membership'] = membership.pk

        return context


    def form_valid(self, form):

        membership = self.object
        if form.cleaned_data["contact_type"] == "organization":
            membership.organization = form.cleaned_data['organization']
        else:
            membership.organization = form.cleaned_data['contact']

        membership.fees = form.cleaned_data['fees']
        membership.state = form.cleaned_data['state']
        membership.currency = form.cleaned_data['currency']
        membership.apply_fees = form.cleaned_data['apply_fees']
        membership.annual_cost = form.cleaned_data['annual_cost']
        membership.renewal_period = form.cleaned_data['renewal_period']
        membership.membership_type = form.cleaned_data['membership_type']
        membership.save()
        add_logentry("membership_manager", "membership", membership.pk, str(membership), self.request.user, 2)

        if membership.free_membership:
            if membership.renews.exists():
                membership.renews.update(active=False)

        formset = modelformset_factory(
            Service, form=MembershipServiceForm, formset=GTBaseModelFormSet,
            can_delete=True, extra=1, can_order=True)

        fset = formset(self.request.POST, queryset=Service.objects.filter(
            membership=membership), prefix="mts")

        if fset.is_valid():
            instances = fset.save(commit=False)
            for delinst in fset.deleted_objects:
                delinst.delete()
            for instance in instances:
                instance.membership = membership
                instance.save()

            if membership.organization.active:
                messages.success(self.request, "Membresía actualizada con éxito")
            else:

                context = {
                    'pk_orga_contact': membership.organization.pk,
                    'type': "organization",
                    'today': timezone.now(),
                    'form_filters': FilterEmailsForm(),
                    'form_template_newsletter': NewsLetterTemplateForm(),
                    'form_template_email': EmailTemplateForm(),
                    'mem_template': MembershipTemplateForm(),
                    'object_list': Membership.objects.all()
                }

                if membership.organization.type:
                    context['type'] = "contact"

                return render(self.request, "membership/membership_list.html", context=context)

        return super().form_valid(form)




@permission_required('membership_manager.add_membership')
def create_membership(request):

    template = request.GET.get('template', None)
    formset = modelformset_factory(
        Service, form=MembershipServiceForm, formset=GTBaseModelFormSet,
        can_delete=True, extra=1, can_order=True)

    # We will save or update
    if request.method == 'POST':

        # create a new object membership
        form = MembershipForm(request.POST)
        fset = formset(request.POST, queryset=Service.objects.none(), prefix="mts")

        # We save the form and the formset
        if form.is_valid() and fset.is_valid():

            organization = form.cleaned_data['organization']
            if form.cleaned_data['contact_type'] == "contact":
                organization = form.cleaned_data['contact']

            membership = Membership(
                membership_type=form.cleaned_data['membership_type'],
                organization=organization,
                annual_cost=form.cleaned_data['annual_cost'],
                currency=form.cleaned_data['currency'],
                renewal_period=form.cleaned_data['renewal_period'],
                state=form.cleaned_data['state'],
                apply_fees=form.cleaned_data['apply_fees'],
                fees=form.cleaned_data['fees'],
                free_membership=form.cleaned_data['free_membership']
            )

            membership.save()

            if membership.free_membership:
                membership.last_renew_start_date = membership.creation_date
                membership.save()

            add_logentry("membership_manager", "membership", membership.pk, str(membership), request.user, 1)

            if not membership.renews.exists() and not membership.free_membership:
                create_renew(membership)

            instances = fset.save(commit=False)
            for instance in instances:
                instance.membership = membership
                instance.save()
            messages.success(request, "Membresía registrada con éxito")
            return redirect('memberships')

        # if there are errors we return the error messages
        else:
            messages.error(
                request,
                "Error al intentar crear la membresía")

    # We will list data or show new form
    if request.method == 'GET':

        # if there is a template load initial data
        if template is not None and template != "":
            m_template = MembershipTemplate.objects.filter(pk=template).first()

            form = MembershipForm(initial={
                'membership_type': m_template.membership_type,
                'state': m_template.state,
                'contact_type': 'organization',
                'currency': m_template.currency,
                'annual_cost': m_template.annual_cost,
                'renewal_period': m_template.renewal_period,
                'free_membership': m_template.free_membership,
            })
            servicesmt = ServiceMT.objects.filter(membership__pk=template)
            templateinitial = []

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
            form = MembershipForm(initial={'contact_type': 'organization'})
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
        object_repr = str(membership)
        object_pk = membership.pk
        membership.delete()
        add_logentry("membership_manager", "membership", object_pk, object_repr, request.user, 3)
        messages.success(request, "Membresía eliminada con éxito")
        return redirect('memberships')


@permission_required('membership_manager.change_membership')
def deactivate_membership(request, pk):
    membership = Membership.objects.filter(pk=pk).first()
    if membership:
        membership.state = "inactive"
        membership.save()
        add_logentry("membership_manager", "membership", membership.pk, str(membership), request.user, 2)
        messages.success(request, "Membresía desactivada con éxito")
        return redirect('memberships')

@permission_required('membership_manager.view_membershiprenew')
def renewals_list(request, pk):
    renewals_list = MembershipRenew.objects.filter(membership__pk=pk).order_by('-start_date')
    return render(request, "membership/renewals.html", context={'renewals_list': renewals_list})