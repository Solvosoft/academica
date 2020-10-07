from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from membership_manager.forms import ContactSearchForm, ContactAddForm
from membership_manager.models import Organization


@method_decorator(permission_required('membership_manager.view_contact'), name='dispatch')
class ContactListView(ListView):
    template_name = "contact/contact_list.html"
    paginate_by = 30

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(ContactListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.form = ContactSearchForm(self.request.GET, initial={'apply_filters': True})
        self.form.is_valid()
        queryset = Organization.objects.filter(type=True)
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
            instance = Organization.objects.get(pk=pk)
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
        contact = Organization.objects.get(pk=pk)
        form = ContactAddForm(initial=contact.__dict__)
    context = {
        'form': form,
    }
    return render(request, 'contact/edit.html', context=context)


@permission_required('membership_manager.delete_contact')
def delete_contacts(request, pk):
    contact = Organization.objects.filter(pk=pk)
    if contact:
        contact.delete()
        messages.success(request, "Contacto eliminado con exíto")
        return redirect('contacts')