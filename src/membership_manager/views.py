from django.apps import apps
from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from async_notifications.models import EmailTemplate, EmailNotification
from async_notifications.tasks import send_email
from membership_core.models import Country, ServiceType
from membership_manager.dashboard import TopStats
from membership_manager.models import Membership, Service, Organization
from membership_manager.newsletterform import EmailTemplateForm, EmailNotificationForm
from membership_telbot_manager.forms import TelegramNotificationTemplateForm, TelegramNotificationTemplateEdit
from membership_telbot_manager.models import TelGroup, TelegramNotificationTemplate
from membership_telbot_manager.utils import expiration_message, memberships, help_dialog, invoices, notification_message
from membership_telbot_manager.views import help, state
from .forms import ServiceTypeForm, LogEntryFilterForm
from .utils import add_logentry


def servicios_stats():
    for service in ServiceType.objects.all():
        yield (service.name, service.service_set.count())


def country_stats():
    for country in Country.objects.all().order_by('name'):
        total = Membership.objects.filter(organization__country=country, state='active').distinct().count()
        if total:
            yield (country.flag, country.name, total)


@login_required
def index(request):
    if request.user.has_perm('membership_manager.can_show_dashboard'):
        context = {'topstat': TopStats(),
                'vencimientoanual_url': reverse('vencimientoanual-list'),
                'pagoanual_url': reverse('pagoanual-list'),
                'countries': country_stats(),
                'servicios_stats': servicios_stats()
                }
        return render(request, 'membership/home.html', context=context)
    return redirect(reverse('courses'))


def email_template(request, pk):

    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)

        if form.is_valid():
            template = form.cleaned_data['email_template']

            if template:
                return redirect('create_email_notification', pk=template.pk, membership=pk)
            else:
                return redirect('create_email_notification', pk=0, membership=pk)


@permission_required('async_notifications.add_emailnotification')
def create_email_notification(request, pk, membership):

    membresia = get_object_or_404(Membership, pk=membership)
    emails = []

    if request.method == "POST":

        form = EmailNotificationForm(request.POST)

        if form.is_valid():
            emailnotification = EmailNotification(
                subject = form.cleaned_data['subject'],
                message = form.cleaned_data['message'],
                bcc = str(", ".join(form.cleaned_data['bcc'].values_list('email', flat=True))),
                cc = str(", ".join(form.cleaned_data['cc'].values_list('email', flat=True))),
                user = request.user,
                recipient = form.cleaned_data['recipient'],
                file = form.cleaned_data['file']
            )
            emailnotification.save()
            obj = EmailNotification.objects.all().last()
            add_logentry("async_notifications", "emailnotification", obj.pk, str(obj), request.user, 1)
            send_email(obj.pk)
            messages.success(request, 'Notificación de correo electrónico generada exitosamente.')
            return redirect('memberships')
    else:

        if membresia.organization:
            emails.append(membresia.organization.email)

        if pk == 0:
            form = EmailNotificationForm(initial={'recipient': ", ".join(emails)})
        else:
            template = get_object_or_404(EmailTemplate, pk=pk)
            form = EmailNotificationForm(initial={'subject':template.subject,
                                                  'message': template.message,
                                                  'recipient': ", ".join(emails)})

    return render(request, "membership/create_email_notification.html", context={'form': form,
                                                                                 'template': pk})

@permission_required('membership_core.view_servicetype')
@permission_required('membership_core.add_servicetype')
def services_list(request):

    if request.method == "POST":
        form = ServiceTypeForm(request.POST)

        if form.is_valid():
            service = form.save()
            add_logentry("membership_core", "servicetype", service.pk, service.name, request.user, 1)
            messages.success(request, "Servicio registrado con éxito")
            return redirect('services_list')
    else:
        form = ServiceTypeForm()

    services_list = ServiceType.objects.all()

    return render(request, "services/services_list.html", context={'form': form, 'service_edit': 0,
                                                                   'services_list': services_list})


@method_decorator(permission_required('membership_core.view_servicetype'), name='dispatch')
@method_decorator(permission_required('membership_core.change_servicetype'), name='dispatch')
class EditService(UpdateView):
    model = ServiceType
    form_class = ServiceTypeForm
    template_name = 'services/services_list.html'
    success_url = reverse_lazy('services_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_edit'] = 1
        context['services_list'] = ServiceType.objects.all()
        return context

    def form_valid(self, form):
        service = form.save()
        add_logentry("membership_core", "servicetype", service.pk, service.name, self.request.user, 2)
        messages.success(self.request, "Servicio actualizado con éxito")
        return super().form_valid(form)


@permission_required('membership_core.view_servicetype')
@permission_required('membership_core.delete_servicetype')
def delete_service(request, pk):
    service = ServiceType.objects.filter(pk=pk).first()

    if service:
        object_pk = service.pk
        object_repr = service.name
        Service.objects.filter(servicetype=service).delete()
        service.delete()
        add_logentry("membership_core", "servicetype", object_pk, object_repr, request.user, 3)
        messages.success(request, "Servicio eliminado con éxito")
        return redirect('services_list')


def logentry_filter_view(request):
    contenttype = None

    if request.method == "POST":
        form = LogEntryFilterForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            if category:
                contenttype = ContentType.objects.filter(pk=int(category)).first()
            return redirect('logentry_list', model=contenttype.model)

    else:
        form = LogEntryFilterForm()


    return render(request, 'logentry_filter.html', context={'form':form})



permission_required('admin.view_logentry')
def logentry_list(request, model):
    logentry_list = LogEntry.objects.filter(content_type__model=model)
    return render(request, 'logentry_list.html', context={'logentry_list': logentry_list})


permission_required('admin.view_logentry')
def logentry_object(request, app, model, pk):

    model_n = apps.get_model(app, model)
    object_n = get_object_or_404(model_n, pk=pk)
    logentry_list = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(object_n).pk, object_id=pk)
    return render(request, 'logentry_list.html', context={'logentry_list': logentry_list})


def send_telegram_notification(request, pk):

    organization = get_object_or_404(Organization, pk=pk)
    group = TelGroup.objects.get(organization=organization)
    form = TelegramNotificationTemplateForm(request.POST)
    form.is_valid()
    template = form.cleaned_data['template_telegram']

    if template:

        if template.name == "Facturas":
            invoices(group.chat_id)

        if template.name == "Membresías":
            memberships(group.chat_id)

        if template.name == "Diálogo de ayuda":
            help_dialog(group.chat_id)

        if template.name == "Mensaje de expiración":
            expiration_message(organization, group.chat_id)

        if template.name == "Mensaje de notificación":
            notification_message(organization, group.chat_id)

        messages.success(request, "Notificación enviada con éxito")

        return redirect('memberships')


def telegram_message_list(request):
    messages_list = TelegramNotificationTemplate.objects.all()
    return render(request, 'membership/telegram_messages_list.html', context={'messages_list': messages_list})

class EditTelegramMessage(UpdateView):

    model = TelegramNotificationTemplate
    template_name = 'membership/edit_telegram_message.html'
    form_class = TelegramNotificationTemplateEdit
    success_url = reverse_lazy('telegram_message_list')


    def form_valid(self, form):
        template = form.save()
        add_logentry("membership_telbot_manager", "telegramnotificationtemplate", template.pk, str(template), self.request.user, 2)
        messages.success(self.request, "Mensaje actualizado con éxito")
        return super().form_valid(form)