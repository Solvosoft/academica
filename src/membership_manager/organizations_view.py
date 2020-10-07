from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from membership_manager.forms import OrganizationSearchForm, OrganizationAddForm
from membership_manager.models import Organization


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