# encoding: utf-8
'''
Created on 18/10/2020

@author: allexiusw
'''
from django.views.generic import ListView, DeleteView
from django.shortcuts import render
from ..models import Bill
from ..forms import BillSearchForm, BillCreateForm
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


@method_decorator(permission_required('bills.view_bill'), name='dispatch')
class BillList(ListView):
    template_name = "bills/bill_list.html"
    model = Bill
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = BillSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['student']:
            queryset = queryset.filter(student__in=self.form.cleaned_data['student'])
        if self.form.cleaned_data['is_paid'] and (int(self.form.cleaned_data['is_paid']) == BillSearchForm.PAID):
            queryset = queryset.filter(is_paid=True)
        elif self.form.cleaned_data['is_paid'] and (int(self.form.cleaned_data['is_paid']) == BillSearchForm.NOT_PAID):
            queryset = queryset.filter(is_paid=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_search'] = BillSearchForm(self.request.GET)
        context['has_data'] = Bill.objects.exists()
        return context

@permission_required('bills.add_bill')
def create_bill(request):
    context = {}
    if request.method == 'POST':
        form = BillCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request, "Factura guardada con éxito")
            return HttpResponseRedirect(reverse('listbills'))
        else:
            messages.error(request, "Error al guardar factura")
    else:
        context['form'] = BillCreateForm()
    return render(request, 'bills/bill_create.html', context)


@permission_required('bills.change_bill')
def edit_bill(request, pk=None):
    context = {}
    if pk is not None:
        if request.method == "POST":
            instance = Bill.objects.get(pk=pk)
            form = BillCreateForm(request.POST, instance=instance)
            if form.is_valid():
                messages.success(request, "Factura guardada con éxito")
                form.save()
                return HttpResponseRedirect(reverse('listbills'))
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'bills/bill_update.html', {'form': form})
        else:
            if request.method == "GET":
                instance = Bill.objects.get(pk=pk)
                form = BillCreateForm(initial=instance.__dict__)
                return render(request, 'bills/bill_update.html', {'form': form})
    return HttpResponseRedirect(reverse('listbills'))


@method_decorator(permission_required('bills.delete_bill'), name='dispatch')
class BillDelete(DeleteView):
    model = Bill
    success_url = reverse_lazy("listbills")
    success_message = "Factura eliminada con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(BillDelete, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(BillDelete, self).form_valid(form)

