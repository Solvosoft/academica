from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.views.generic import ListView, UpdateView

from membership_manager.forms import InvoiceChangeForm, InvoicePayForm
from membership_manager.models import Invoice
from membership_manager.newsletterform import FilterEmailsForm


@method_decorator(permission_required('membership_manager.view_invoice'), name='dispatch')
class InvoiceListView(ListView):
    model = Invoice
    template_name = 'membership/invoice_list.html'
    ordering = 'creation_date'

    def get_year_filter(self):
        year = self.request.GET.get('year', now().year)
        try:
            year=int(year)
        except ValueError:
            year = now().year
        return year

    def filter_queryset(self, queryset):
        self.form = FilterEmailsForm(self.request.GET)
        self.form.is_valid()

        filters = {}
        if self.form.cleaned_data['name']:
            filters['membership__organization__in'] = list(self.form.cleaned_data['name'].values_list('pk', flat=True))
        if self.form.cleaned_data['state']:
            filters['membership__state'] = self.form.cleaned_data['state']

        if self.form.cleaned_data['country']:
            filters['membership__organization__country__in']=list(
                self.form.cleaned_data['country'].values_list('pk', flat=True))

        if self.form.cleaned_data['currency']:
            filters['currency__in'] = self.form.cleaned_data['currency']

        if self.form.cleaned_data['payment_method']:
            filters['payment_method__in'] = self.form.cleaned_data['payment_method']

        if self.form.cleaned_data['membership_type']:
            filters['membership__membership_type__in'] = self.form.cleaned_data['membership_type']

        if self.form.cleaned_data['service_type']:
            filters['membership__service__servicetype__in'] = self.form.cleaned_data['service_type']

        if self.form.cleaned_data['invoices']:
            filters['status'] = self.form.cleaned_data['invoices']

        return queryset.filter(**filters)

    def get_queryset(self):
        queryset = self.filter_queryset(super().get_queryset())

        self.years = queryset.dates('expiration_date', 'year')
        self.current_year = self.get_year_filter()
        queryset = queryset.filter(expiration_date__year=self.current_year).order_by('expiration_date')

        dev = [(d.month, queryset.filter(expiration_date__month=d.month)) for d in queryset.dates('expiration_date', 'month')]
        return reversed(dev)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['years'] = self.years
        context['current_year'] = self.current_year
        context['form_filters'] = self.form
        context['params'] = self.get_pagination_params()
        return context

    def get_pagination_params(self):
        params=''
        for key in self.form.cleaned_data:
            if key not in ['year', 'apply_filters', 'search_in', 'payment_method', 'apply_fees']:
                if key in ['state', 'invoices']:
                    params += "&%s=%s" % (key, self.form.cleaned_data[key])
                else:
                    if isinstance(self.form.cleaned_data[key], list):
                        data = self.form.cleaned_data[key]
                    else:
                        data = self.form.cleaned_data[key].values_list('pk', flat=True)
                    for item in data:
                        params += "&%s=%s" % (key, item)
        return params


@method_decorator(permission_required('membership_manager.change_invoice'), name='dispatch')
class InvoiceChangeView(UpdateView):
    model = Invoice
    template_name = 'membership/invoice_form.html'
    form_class = InvoiceChangeForm
    #ordering = 'creation_date'
    success_url = reverse_lazy('invoice-list')

    def get_next(self):
        urlb64 = self.request.GET.get('next', '')
        if urlb64:
            url = urlsafe_base64_decode(urlb64).decode()
        else:
            url = reverse_lazy('invoice-list')
        return url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial']={
            'next': self.get_next()
        }
        return kwargs

    def get_context_data(self, **kwargs):
        context=super().get_context_data()
        context['title'] = 'Editar factura'
        return context

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, "Factura guardada satisfactoriamente")
        return HttpResponseRedirect(form.cleaned_data['next'])


@method_decorator(permission_required('membership_manager.change_invoice'), name='dispatch')
class InvoicePayView(UpdateView):
    model = Invoice
    template_name = 'membership/invoice_form.html'
    form_class = InvoicePayForm
    #ordering = 'creation_date'
    success_url = reverse_lazy('invoice-list')

    def get_next(self):
        urlb64 = self.request.GET.get('next', '')
        if urlb64:
            url = urlsafe_base64_decode(urlb64).decode()
        else:
            url = reverse_lazy('invoice-list')
        return url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial']={
            'payment_date': now(),
            'next': self.get_next()
        }
        return kwargs

    def get_context_data(self, **kwargs):
        context=super().get_context_data()
        context['title'] = 'Pago de factura'
        return context

    def form_valid(self, form):
        super().form_valid(form)
        self.object.status = 'paid'
        self.object.save()
        messages.success(self.request, "Factura pagada satisfactoriamente")
        return HttpResponseRedirect(form.cleaned_data['next'])