from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.urls import reverse

from async_notifications.models import EmailTemplate, EmailNotification
from async_notifications.tasks import send_email
from membership_core.models import Country, ServiceType
from membership_manager.dashboard import TopStats
from membership_manager.models import Membership
from membership_manager.newsletterform import EmailTemplateForm, EmailNotificationForm
from .news_letter_view import NewsLetter


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


@permission_required('async_notifications.delete_newsletter')
def delete_membership_service(request, pk):
    boletin = NewsLetter.objects.filter(pk=pk).first()
    if boletin:
        boletin.delete()
        return redirect('news_letter_list')


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