from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.forms import modelformset_factory
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic import ListView
from djgentelella.forms.forms import GTBaseModelFormSet

from membership_core.models import MembershipTemplate, ServiceMT
from membership_manager.forms import MembershipServiceForm, MembershipForm, MembershipTemplateForm
from membership_manager.models import Membership, Service
from membership_manager.newsletterform import FilterEmailsForm, NewsLetterTemplateForm, \
    EmailTemplateForm


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
            queryset = self.form.cleaned_data['name']
        if self.form.cleaned_data['state']:
            filters['state'] = self.form.cleaned_data['state']

        if self.form.cleaned_data['country']:
            queryset = queryset.filter(organization__country__in=self.form.cleaned_data['country'])

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
        context['mem_template'] = MembershipTemplateForm()
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
    template = request.GET.get('template', None)
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
        if template is not None and template != "":
            m_template = MembershipTemplate.objects.get(pk=template).__dict__
            form = MembershipForm(initial=m_template)
            servicesmt = ServiceMT.objects.filter(membership__pk=template)
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
