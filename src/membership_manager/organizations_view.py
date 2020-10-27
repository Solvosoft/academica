from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView

from membership_manager.forms import OrganizationSearchForm, OrganizationAddForm, ContactOrganizationForm, ContactsForm
from membership_manager.models import Organization, Membership
from membership_manager.utils import add_logentry


@method_decorator(permission_required('membership_manager.view_organization'), name='dispatch')
class OrganizationListView(ListView):
    template_name = "organization/organization_list.html"
    paginate_by = 30

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(OrganizationListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.form = OrganizationSearchForm(self.request.GET)
        self.form.is_valid()
        queryset = Organization.objects.filter(type=False).order_by("-active", "name")
        if self.form.cleaned_data['organization']:
            queryset = queryset.filter(pk__in=self.form.cleaned_data['organization'])
        if self.form.cleaned_data['countries']:
            queryset = queryset.filter(country__in=self.form.cleaned_data['countries'])
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
        contactsForm = ContactsForm(request.POST)

        # We save the form
        if form.is_valid():
            organization = form.save()

            if contactsForm.is_valid():
                if contactsForm.cleaned_data['contacts']:
                    organization.contacts.add(*contactsForm.cleaned_data['contacts'])

            add_logentry("membership_manager", "organization", organization.pk, str(organization), request.user, 1)
            messages.success(request, "Organización registrada con éxito")
            return redirect('organizations')

        # if there are errors we return the error messages
        else:
            messages.error(
                request,
                "Error al intentar guardar la organización")


    else:
        form = OrganizationAddForm(initial={'type':False})
        contactsForm = ContactsForm()

    context = {
        'form': form,
        'contactsForm': contactsForm
    }
    return render(request, 'organization/create.html', context=context)


@method_decorator(permission_required('membership_manager.change_organization'), name='dispatch')
class EditOrganization(UpdateView):
    model = Organization
    form_class = OrganizationAddForm
    template_name = 'organization/edit.html'
    success_url = reverse_lazy('organizations')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = context['object']
        context['contactsForm'] = ContactsForm(initial={'contacts': organization.contacts.all()})
        context['organization'] = organization.pk
        return context

    def form_valid(self, form):

        if form.cleaned_data['active']:
            Membership.objects.filter(organization=self.object).update(state="active")

        else:
            Membership.objects.filter(organization=self.object).update(state="inactive")

        organization = form.save()

        contactsForm = ContactsForm(self.request.POST)

        if contactsForm.is_valid():
            if contactsForm.cleaned_data['contacts']:
                organization.contacts.remove(*organization.contacts.all())
                organization.contacts.add(*contactsForm.cleaned_data['contacts'])

        add_logentry("membership_manager", "organization", organization.pk, str(organization), self.request.user, 2)
        messages.success(self.request, "Organización actualizada con éxito")
        return super().form_valid(form)


@permission_required('membership_manager.delete_organization')
def delete_organization(request, pk):
    organization = Organization.objects.filter(pk=pk).first()

    if organization:
        object_repr = str(organization)
        object_pk = organization.pk
        organization.delete()
        add_logentry("membership_manager", "organization", object_pk, object_repr, request.user, 3)
        messages.success(request, "Organización eliminada con éxito")
        return redirect('organizations')


@permission_required('membership_manager.change_organization')
def deactivate_organization(request, pk):
    organization = Organization.objects.filter(pk=pk).first()

    if organization:
        organization.active = False
        organization.save()
        add_logentry("membership_manager", "organization", organization.pk, str(organization), request.user, 2)
        Membership.objects.filter(organization=organization).update(state="inactive")
        messages.success(request, "Organización desactivada con éxito")
        return redirect('organizations')