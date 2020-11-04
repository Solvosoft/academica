# encoding: utf-8
'''
Created on 18/10/2020

@author: allexiusw
'''
from django.views.generic import ListView, DeleteView
from django.shortcuts import render
from matricula.models import Student
from ..models import ColonExchange, Bill
from ..forms import ColonExchangeCreateForm, BillSearchForm, BillCreateForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator


@method_decorator(permission_required('bills.view_colonexchange'), name='dispatch')
class ColonExchangeList(ListView):
    template_name = "colonexchange/colonexchange_list.html"
    model = ColonExchange
    paginate_by = 30

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(ColonExchangeList, self).dispatch(*args, **kwargs)


@permission_required('bills.add_colonexchange')
def create_colonexchange(request):
    context = {}
    if request.method == 'POST':
        form = ColonExchangeCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request, "Moneda de intercambio guardada con éxito")
            return HttpResponseRedirect(reverse('colonexchange'))
        else:
            messages.error(request, "Error al guardar moneda de intercambio")
    else:
        context['form'] = ColonExchangeCreateForm()
    return render(request, 'colonexchange/colonexchange_create.html', context)


@method_decorator(permission_required('bills.delete_colonexchange'), name='dispatch')
class ColonExchangeDelete(DeleteView):
    model = ColonExchange
    success_url = "/matricula_bills/colonexchanges"
    success_message = "Moneda de intercambio eliminada con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(ColonExchangeDelete, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(ColonExchangeDelete, self).delete(request, *args, **kwargs)


@permission_required('bills.change_colonexchange')
def edit_colonexchange(request, pk=None):
    if pk is not None:
        if request.method == "POST":
            instance = ColonExchange.objects.get(pk=pk)
            form = ColonExchangeCreateForm(request.POST, instance=instance)
            if form.is_valid():
                messages.success(request, "Moneda de intercambio guardada con éxito")
                form.save()
                return HttpResponseRedirect(reverse('colonexchange'))
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'colonexchange/colonexchange_update.html', {'form': form})
        else:
            if request.method == "GET":
                instance = ColonExchange.objects.get(pk=pk)
                form = ColonExchangeCreateForm(initial=instance.__dict__)
                return render(request, 'colonexchange/colonexchange_update.html', {'form': form})
    return HttpResponseRedirect(reverse('colonexchange'))


@method_decorator(permission_required('bills.view_bill'), name='dispatch')
class BillList(ListView):
    template_name = "bills/bill_list.html"
    model = Bill
    paginate_by = 30

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(BillList, self).dispatch(*args, **kwargs)

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
    success_url = "/matricula_bills/list"
    success_message = "Factura eliminada con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(BillDelete, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(BillDelete, self).delete(request, *args, **kwargs)

