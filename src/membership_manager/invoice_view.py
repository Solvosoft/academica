from django.contrib import messages
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.auth.decorators import permission_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from django.views.generic import ListView, UpdateView

from membership_manager.forms import InvoiceChangeForm, InvoicePayForm
from membership_manager.invoice_utils import pay_invoice, regenerate_invoice_pdf, regenerate_invoice_code, \
    send_paid_invoice
from membership_manager.models import Invoice
from membership_manager.newsletterform import FilterEmailsForm, NewsLetterTemplateForm
from membership_manager.utils import add_logentry
from membership_telbot_manager.utils import get_telegram_group
from membership_telbot_manager.views import send_notification_message, send_invoice_message


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
        context['form_template_newsletter'] = NewsLetterTemplateForm()
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
        invoice = context['object']
        context['title'] = 'Editar factura'
        context['invoice'] = invoice.pk
        return context

    def form_valid(self, form):
        super().form_valid(form)
        invoice = form.save()
        add_logentry("membership_manager", "invoice", invoice.pk, str(invoice), self.request.user, 2)
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
        form.save()

        membership = self.object.membership
        pay_invoice(self.object)
        LogEntry.objects.log_action(
            user_id=self.request.user.pk,
            content_type_id=ContentType.objects.get_for_model(membership).pk,
            object_id=membership.pk,
            object_repr="Pago de membresía realizado.",
            action_flag=CHANGE
        )
        if membership.organization:
            if not membership.organization.type:
                telgroup = get_telegram_group(membership)
                if telgroup:
                    send_notification_message(telgroup.chat_id, membership.organization)
                    if self.object.pdf_invoice:
                        send_invoice_message(telgroup.chat_id, self.object.pdf_invoice)

        messages.success(self.request, "Factura pagada satisfactoriamente")
        return HttpResponseRedirect(form.cleaned_data['next'])


@permission_required('membership_manager.change_invoice')
def invoiceAction(request):
    action = request.POST.get('oper')
    obj = request.POST.get('pk')
    ok='Error'
    if action and obj:
        queryset = Invoice.objects.filter(pk=obj)

        if action == "NP":
            send_paid_invoice(queryset, request, 'pay_mail')
            ok='ok'
            messages.success(request, "Correo enviado")
        elif action == "ER":
            send_paid_invoice(queryset, request, 'notification_mail')
            ok='ok'
            messages.success(request, "Correo enviado")
        elif action == "RC":
            regenerate_invoice_code(queryset, request)
            ok='ok'
            messages.success(request, "Código de factura regenerado correctamente")
        elif action == "RP":
            regenerate_invoice_pdf(queryset, request)
            ok='ok'
            messages.success(request, "PDF regenerado correctamente")

    return JsonResponse({'result': ok})