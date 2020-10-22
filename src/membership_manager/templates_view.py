from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.views.generic import ListView, UpdateView
from membership_manager.forms import OrganizationAddForm,\
    ContactOrganizationForm, TemplateSearchForm, TemplateAddForm
from membership_core.models import MembershipTemplate
from membership_manager.models import Organization


@method_decorator(permission_required('membership_core.view_membershiptemplate'), name='dispatch')
class TemplateListView(ListView):
    template_name = "template/template_list.html"
    paginate_by = 30
    model = MembershipTemplate

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(TemplateListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        self.form = TemplateSearchForm(self.request.GET)
        self.form.is_valid()
        queryset = MembershipTemplate.objects.all().order_by('name')
        if self.form.cleaned_data['name']:
            queryset = queryset.filter(
                Q(name__icontains=self.form.cleaned_data['name']) |
                Q(description__icontains=self.form.cleaned_data['name']))
        if self.form.cleaned_data['currency']:
            queryset = queryset.filter(currency__in=self.form.cleaned_data['currency'])
        if self.form.cleaned_data['renewal_period']:
            queryset = queryset.filter(renewal_period__in=self.form.cleaned_data['renewal_period'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formsearch'] = TemplateSearchForm(self.request.GET)
        return context


@permission_required('membership_core.add_membershiptemplate')
def create_template(request):
    if request.method == 'POST':
        form = TemplateAddForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Plantilla registrada con éxito")
            return redirect('templates')
        else:
            messages.error(request, "Error al guardar la plantilla")
    else:
        form = TemplateAddForm()
    context = {
        'form': form
    }
    return render(request, 'template/create.html', context=context)


@method_decorator(permission_required('membership_core.change_membershiptemplate'), name='dispatch')
class EditTemplate(UpdateView):
    model = MembershipTemplate
    form_class = TemplateAddForm
    template_name = 'template/edit.html'
    success_url = reverse_lazy('templates')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        template = context['object']
        context['template_form'] = TemplateAddForm(instance=template)
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Plantilla actualizada con éxito")
        return super().form_valid(form)


@permission_required('membership_core.delete_membershiptemplate')
def delete_template(request, pk):
    template = MembershipTemplate.objects.filter(pk=pk).first()
    if template:
        template.delete()
        messages.success(request, "Plantilla eliminada con éxito")
        return redirect('templates')
