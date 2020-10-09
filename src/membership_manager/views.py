from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from async_notifications.models import EmailTemplate, EmailNotification
from async_notifications.tasks import send_email
from membership_core.models import Country, ServiceType
from membership_manager.dashboard import TopStats
from membership_manager.models import Membership
from membership_manager.newsletterform import EmailTemplateForm, EmailNotificationForm
from .forms import ServiceTypeForm


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
    context = {'topstat': TopStats(),
               'vencimientoanual_url': reverse('vencimientoanual-list'),
               'pagoanual_url': reverse('pagoanual-list'),
               'countries': country_stats(),
               'servicios_stats': servicios_stats()
               }
    return render(request, 'membership/home.html', context=context)

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
            form.save()
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


@permission_required('membership_core.view_servicetype')
@permission_required('membership_core.delete_servicetype')
def delete_service(request, pk):
    service = ServiceType.objects.filter(pk=pk).first()

    if service:
        service.delete()
        return redirect('services_list')