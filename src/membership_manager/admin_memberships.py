from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect
from django.views.generic import ListView

from membership_manager.forms import MembInvPaymentsForm
from membership_manager.models import Membership, Invoice
from membership_manager.utils import membership_filter


def payments_history(modeladmin, request, queryset):
    id_list = []
    for membership in queryset:
        id_list.append(membership.pk)
    return HttpResponseRedirect("/payments/" + f"?ids={id_list}")


payments_history.short_description = "Mostrar Historial de Pagos"


class MembershipNotificationFilter(SimpleListFilter):
    title = 'Invoices Renewals'  # a label for our filter
    parameter_name = 'renews'  # you can put anything here

    def lookups(self, request, model_admin):
        # This is where you create filter options; we have two:
        return [
            ('30', '30 days to pay'),
            ('15', '15 days to pay'),
            ('7', '7 days to pay'),
            ('0', 'day to pay'),
        ]

    def queryset(self, request, queryset):
        # This is where you process parameters selected by use via filter options:
        value=self.value()
        if value is None:
            value=False
        return membership_filter(queryset, filt=value)


class MembInvoices(ListView):
    template_name = 'admin/membership_admin/invoice/change_list.html'
    form_class = MembInvPaymentsForm
    filter_options = {'pending': 'pendientes', 'paid': 'pagadas', 'inactive': 'inactivas'}

    def get_paid_value(self, object_dict):
        cont = 0
        pending_amount = 0
        for item in object_dict['results']:
            if item.status == 'paid':
                cont += item.amount
            elif item.status == 'pending':
                pending_amount += item.amount
        object_dict['paid'] = cont
        object_dict['pending'] = pending_amount
        return object_dict

    def filter_queryset(self, ids, queryset, filter_option=None):
        new_tmp_list = []
        for id in ids:
            tmp_dict = []
            object_dict = {'name': '', 'paid': 0, 'pending': 0}
            for inv in queryset:
                if inv.membership.pk == int(id):
                    if object_dict['name'] == '':
                        object_dict['name'] = inv.membership.name
                    tmp_dict.append(inv)
            if len(tmp_dict) >= 1:
                object_dict['results'] = tmp_dict
                object_dict = self.get_paid_value(object_dict)
                new_tmp_list.append(object_dict)
            else:
                object_dict['no_results'] = 'No hay facturas'
                new_tmp_list.append(object_dict)
                tmp_membship = Membership.objects.filter(pk=id)
                object_dict['name'] = tmp_membship.name
            if filter_option is not None:
                object_dict['filter_option'] = filter_option
        return new_tmp_list

    def get_queryset(self):
        q = self.request.GET.get('ids')
        if q:
            res = q.strip('][').split(', ')
            queryset = Invoice.objects.filter(membership__in=res)
            return queryset
        return Invoice.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(MembInvoices, self).get_context_data(**kwargs)
        if not object_list:
            ids = self.request.GET.get('ids')
            q = ids.strip('][').split(', ')
            qset = context['object_list']
            context['form'] = self.form_class()
            context['object_list'] = self.filter_queryset(q, qset)
        else:
            context['object_list'] = object_list
        context['cl'] = {
            'opts': {
                'app_label': 'membership_manager',
                'verbose_name_plural': 'Historiales de membresías',
                'app_config': {
                    'verbose_name': 'Membresias',

                }
            }
        }
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        form = self.form_class(self.request.POST or None)
        q = self.request.GET.get('ids')
        ids = q.strip('][').split(', ')
        if form.is_valid():
            tmp_qset = self.object_list.filter(status=form.cleaned_data['option'])
            new_qset = self.filter_queryset(ids, tmp_qset, self.filter_options[form.cleaned_data['option']])
            return self.render_to_response(self.get_context_data(object_list=new_qset, form=form))
        return self.render_to_response(self.get_context_data(object_list=self.object_list, form=form))
