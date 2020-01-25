import csv

from async_notifications.utils import send_email_from_template
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import FieldDoesNotExist
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, TemplateView
from django.contrib import messages
from membership_manager.Simulador import ManejadorNotificaciones
from membership_manager.forms import MembInvPaymentsForm
from membership_manager.invoice_utils import create_invoice
from membership_manager.models import Membership, Invoice, Organization, MembershipRenew
from membership_manager.tasks import task_membership_deactivating_membership
from membership_manager.utils import get_emails


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



def get_headers(modeladmin, queryset):
    data = []
    klass = queryset.model
    for field in modeladmin.fields:
        if hasattr(modeladmin, field):
            data.append(getattr(modeladmin, field).short_description)
        elif hasattr(klass, field):
            try:
                data.append(klass._meta.get_field(field).verbose_name)
            except FieldDoesNotExist:
                data.append(field)
        else:
            data.append(field)
    return data

def export_csv_fields(modeladmin, request, queryset):
    name = queryset.model.__name__
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="'+name+'.csv"'
    writer = csv.writer(response,  delimiter=';', quotechar='"')
    writer.writerow(get_headers(modeladmin, queryset))

    for obj in queryset:
        data=[]
        for field in modeladmin.fields:
            if hasattr(modeladmin, field):
                data.append(getattr(modeladmin, field)(obj))
            elif hasattr(obj, field):
                data.append(getattr(obj, field))
            else:
                data.append('')
        writer.writerow(data)
    return response
export_csv_fields.short_description = "Exporta a CSV"

def send_email_vencimiento(modeladmin, request, queryset):
    for membership in queryset:
        task_membership_deactivating_membership.delay(membership.pk, True)

send_email_vencimiento.short_description = "Envíar correo de vencimiento de las membresías"


def buscar_inconsistencias(modeladmin, request, queryset):
    return redirect('simulate')

buscar_inconsistencias.short_description = "Busca inconsistencias en las membresías (desarrollo)"


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


@method_decorator(staff_member_required, name='dispatch')
class SimulateNotifications(TemplateView):
    template_name = 'admin/membership_admin/simulatenotifications.html'
    def get_context_data(self, **kwargs):
        context = super(SimulateNotifications, self).get_context_data(**kwargs)
        context['simulador'] = ManejadorNotificaciones()
        return context

@staff_member_required
def repair_membership(request, pk, action):
    if pk == '0' :
        if action == 'graceperiod':
            queryset = Membership.objects.filter(
              state="active", renews__graceperiod=True, renews__active=True)
        elif action == 'invoice':
            queryset = Membership.objects.filter(
                Q(state="active") | Q(state='graceperiod'),
                renews__graceperiod=False, renews__active=True, renews__inv_m_renews=None)
        elif action == '2active':
            queryset = Membership.objects.filter(
                Q(state="active") | Q(state='graceperiod'),
            ).annotate(totalmemb=Count('renews', filter=Q(renews__graceperiod=False, renews__active=True))).filter(
                totalmemb__gt=2
            )
        elif action == '2renews':
            queryset = Membership.objects.filter(Q(state="active") | Q(state='graceperiod'),
                                                 renews__graceperiod=True,
                                                 renews__active=True)
    else:
        mem = get_object_or_404(Membership, pk=pk)
        queryset = [mem]
    for mem in queryset:
        if action == '2active':
            mem.renews.filter(graceperiod=False).update(active=False)
            lastmemb = mem.renews.filter(graceperiod=False).order_by('end_date').last()
            lastmemb.active = True
            lastmemb.save()
        if action == 'graceperiod':
            mem.state = 'graceperiod'
            mem.save()
        if action == '2renews':
            if mem.renews.filter(active=True).count() != 2:
                periodo = mem.renews.filter(active=True, graceperiod=True).order_by('end_date').last()
                lastmemb = mem.renews.filter(graceperiod=False).order_by('end_date').last()
                if lastmemb is not None and periodo is not None:
                    mem.renews.update(active=False)
                    lastmemb.active=True
                    lastmemb.save()
                    periodo.active=True
                    periodo.save()
                else:
                    messages.warning(request, 'Lo lamentamos esta membresía "'+str(mem)+'" no se puede reparar automáticamente')
        if action == 'invoice':
            task_membership_deactivating_membership.delay(mem.pk, False)

    if action == 'invoice':
        messages.info(request,
                         'Debe esperar un tiempo prudencial mientras se ejecutan las tareas para que se refleje')

    return redirect('simulate')

@staff_member_required
def generate_invoice(request, pk):
    renew = get_object_or_404(MembershipRenew, pk=pk)
    invoice = create_invoice(renew)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+invoice.code+'.pdf"'
    response.write(invoice.pdf_invoice.read())
    return response

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
