from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView

from membership_manager.forms import ContactSearchForm, ContactAddForm
from membership_manager.models import Organization


@method_decorator(permission_required('membership_manager.view_organization'), name='dispatch')
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


@permission_required('membership_manager.add_organization')
def create_contacts(request):

    # We create a new contact
    if request.method == 'POST':

        # create a new contact object
        form = ContactAddForm(request.POST)

        # We save the form and the formset
        if form.is_valid():
            form.save()
            messages.success(request, "Contacto registrado con éxito")
            return redirect('contacts')

        # if there are errors we return the error messages
        else:
            messages.error(
                request,
                "Error al intentar guardar el contacto")

    # We display new contact form
    if request.method == 'GET':
        form = ContactAddForm(initial={'type':True, 'active': True})

    context = {
        'form': form
    }
    return render(request, 'contact/create.html', context=context)


@method_decorator(permission_required('membership_manager.change_organization'), name='dispatch')
class EditContact(UpdateView):
    model = Organization
    form_class = ContactAddForm
    template_name = 'contact/edit.html'
    success_url = reverse_lazy('contacts')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Contacto actualizado con éxito")
        return super().form_valid(form)


@permission_required('membership_manager.delete_organization')
def delete_contacts(request, pk):
    contact = Organization.objects.filter(pk=pk)
    if contact:
        contact.delete()
        messages.success(request, "Contacto eliminado con éxito")
        return redirect('contacts')