from async_notifications.utils import send_email_from_template
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from membership_manager.forms import MembInvPaymentsForm
from membership_manager.models import Membership, Invoice, Organization
from membership_manager.utils import membership_filter
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def validateEmail( email ):
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

def get_emails(membership):
    emails = []
    if membership.contact:
        if validateEmail(membership.contact.email):
            emails.append(membership.contact.email )
    if membership.organization:
        if validateEmail(membership.organization.email):
            emails.append(membership.organization.email )
    if emails:
        emails = list(set(emails))
    return emails

def send_email_to_owner(modeladmin, request, queryset):
    for membership in queryset:
        emails = get_emails(membership)
        if emails:
            send_email_from_template('admin_to_membership_mail', emails,
                                     context={
                                         'membership': membership
                                     },
                                     enqueued=True,
                                     user=None,
                                     upfile=None)

send_email_to_owner.short_description = "Envíar correo a responsables de las membresías"

def membership_payments_history(modeladmin, request, queryset):
    id_list = []
    for membership in queryset:
        id_list.append(membership.pk)
    return HttpResponseRedirect("/payments/membership/" + f"?ids={id_list}")
membership_payments_history.short_description = "Historial de pagos"

def organization_payments_history(modeladmin, request, queryset):
    id_list = []
    for membership in queryset:
        id_list.append(membership.pk)
    return HttpResponseRedirect("/payments/organization/" + f"?ids={id_list}")

organization_payments_history.short_description = "Historial de pagos"
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

@method_decorator(staff_member_required, name='dispatch')
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
            object_dict = {'name': '', 'paid': 0, 'pending': 0,'pk':0}
            for inv in queryset:
                if inv.membership.pk == int(id):
                    if object_dict['name'] == '':
                        object_dict['name'] = inv.membership.name
                        object_dict['pk'] = inv.membership.pk
                    tmp_dict.append(inv)
            if len(tmp_dict) >= 1:
                object_dict['results'] = tmp_dict
                object_dict = self.get_paid_value(object_dict)
                new_tmp_list.append(object_dict)
            else:
                object_dict['no_results'] = 'No hay facturas'
                tmp_membship = Membership.objects.get(pk=id)
                object_dict['name'] = tmp_membship.name
                object_dict['pk'] = tmp_membship.pk
                new_tmp_list.append(object_dict)
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
                'verbose_name_plural': 'Historial de pagos de membresias',
                'app_config': {
                    'verbose_name': 'Membresías',

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

@method_decorator(staff_member_required, name='dispatch')
class OrganizationInvoices(ListView):
    template_name = 'admin/membership_admin/organization/change_list.html'
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
            object_dict = {'name': '', 'paid': 0, 'pending': 0,'pk':0}
            for inv in queryset:
                if inv.membership.organization.pk == int(id):
                    if object_dict['name'] == '':
                        object_dict['name'] = inv.membership.organization.name
                        object_dict['pk'] = inv.membership.organization.pk
                    tmp_dict.append(inv)
            if len(tmp_dict) >= 1:
                object_dict['results'] = tmp_dict
                object_dict = self.get_paid_value(object_dict)
                new_tmp_list.append(object_dict)
            else:
                object_dict['no_results'] = 'No hay facturas'
                tmp_org = Organization.objects.get(pk=id)
                object_dict['name'] = tmp_org.name
                object_dict['pk'] = tmp_org.pk
                new_tmp_list.append(object_dict)
            if filter_option is not None:
                object_dict['filter_option'] = filter_option
        return new_tmp_list

    def get_queryset(self):
        q = self.request.GET.get('ids')
        if q:
            res = q.strip('][').split(', ')
            queryset = Invoice.objects.filter(membership__organization__in=res)
            return queryset
        return Invoice.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(OrganizationInvoices, self).get_context_data(**kwargs)
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
                'verbose_name_plural': 'Historial de pagos  de organizaciones',
                'app_config': {
                    'verbose_name': 'Organizaciones',

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
