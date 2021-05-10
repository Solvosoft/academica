# encoding: utf-8

'''
Created on 17/5/2015

@author: luisza
'''
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.contrib import messages
from django.conf import settings

from django_ajax.decorators import ajax

from async_notifications.utils import send_email_from_template

from matricula.models import Group, Enroll


@ajax
@login_required
def enrollme(request, pk):
    group = get_object_or_404(Group, pk=pk)
    student = request.user.student
    all_enrolls = Enroll.objects.filter(group=group, enroll_finished=True)
    all_enrolls = all_enrolls.filter(Q(paid_excluded=True) | Q(bill__is_paid=True) | Q(bill_created=True))
    if all_enrolls.exists() and all_enrolls.count() >= all_enrolls.first().group.maximum \
        and not all_enrolls.filter(student=student).exists():
        return { 
                    "inner-fragments": {
                        "#count_" + str(group.pk): group.enroll_set.count(),
                        "#group_message": '<div class="alert alert-error" role="alert">' + str(_('The group is full and was not possible to enroll you.')) + '</div>'
                    },
                }
    list_enroll = Enroll.objects.filter(group=group, student=student)
    schema = request.scheme+"://"
    if not list_enroll.exists():
        try:
            template = 'email_enroll_success'
            with transaction.atomic():
                enroll = Enroll.objects.create(group=group, student=student)
                if group.in_enrollment or group.in_preenrollment and group.flow == group.AUTO_ENROLL:
                    enroll.enroll_activate = True
                    enroll.enroll_finished = True
                    enroll.save()
                    send_email_from_template(
                        template, [request.user.email],
                        {
                            "url": request.build_absolute_uri(reverse('enrollment')),
                            "group": group,
                            'domain': schema+request.get_host(),
                            'hours_to_pay': settings.HOURS_TO_PAY,
                        },
                        enqueued=False, user=None)
                    if not group.is_paid:
                        message = _("Enrollment success.")
                    else:
                        message = str(_('Enrollment success you have '))+str(settings.HOURS_TO_PAY)+str(_(' hours from now to complete the payment')) +' <a class="btn btn-success" href="'+ reverse('bills')+'">'+str(_('Pay Now')) +'</a>'
                    return { 
                        "inner-fragments": {
                            "#count_" + str(group.pk): group.enroll_set.count(),
                            "#group_message": '<div class="alert alert-info" role="alert">' + str(message) + '</div>'
                        },
                    }
                elif group.in_preenrollment:
                    if group.flow == group.AUTO_PREENROLL:
                        enroll.enroll_activate = True
                    enroll.save()
                    template = 'email_preenroll_success'
                    send_email_from_template(
                        template, [request.user.email],
                        {
                            "url": request.build_absolute_uri(reverse('enrollment')),
                            "group": group,
                            'domain': schema+request.get_host(),
                        },
                        enqueued=False, user=None)
                    return { 
                        "inner-fragments": {
                            "#count_" + str(group.pk): group.enroll_set.count(),
                            "#group_message": '<div class="alert alert-success" role="alert">' + str(_('Pre-enrollment success')) + '</div>'
                        },
                    }
                
        except IntegrityError:
            return { "inner-fragments": {"#count_" + str(group.pk): group.enroll_set.count(),
                                        "#group_message": '<div class="alert alert-info" role="alert">' + str(_('We have some problems with your enroll, try again')) + ' </div>'
                                        },
                    }
    else:
        enroll = list_enroll.first()
        if enroll.group.in_enrollment:
            if not enroll.rejected:
                if not enroll.enroll_finished:
                    enroll.enroll_finished = True
                    enroll.enllod_activated = True
                    enroll.save()
                    send_email_from_template(
                        'email_enroll_success', [request.user.email],
                        {
                            "url": request.build_absolute_uri(reverse('enrollment')),
                            "group": group,
                            'domain': schema+request.get_host(),
                            'hours_to_pay': settings.HOURS_TO_PAY,
                        },
                        enqueued=False, user=None)
                    if enroll.group.is_paid:
                        message = _('Enrollment success you have ')+str(settings.HOURS_TO_PAY)+_(' hours from now to complete the payment') +' <a class="btn btn-success" href="'+ reverse('bills')+'">'+str(_('Pay Now')) +'</a>'
                    else:
                        message = _("Enrollment success.")
                elif enroll.paid_excluded or enroll.bill_set.first() and enroll.bill_set.first().is_paid or not group.is_paid:
                    message = _('You are already enrolled')
                else:
                    message = _('You are enrolled but the paid is pending, if you don\'t paid your enroll will be removed')
            else:
                message = _('Sorry your pre-enroll was rejected')
        elif enroll.group.in_preenrollment:
            if not enroll.rejected:
                message = _('You are already pre-enrolled')
            else:
                message = _('Sorry your pre-enroll was rejected')
        return { 
            "inner-fragments": {
                "#count_" + str(group.pk): group.enroll_set.count(),
                "#group_message": '<div class="alert alert-info" role="alert">' + str(message) + '</div>'
            },
        }


@login_required
def list_enroll(request):
    is_student = hasattr(request.user, 'student')
    context = {
        'list_enroll': Enroll.objects.none(),
        'finished_enroll': Enroll.objects.none(),
        'list_pre': Enroll.objects.none(),
        'student': is_student,
    }
    if is_student:
        student = request.user.student
        context['list_enroll'] = Enroll.objects.filter(
            student=student, enroll_activate=True, enroll_finished=False)
        context['list_pre']  = Enroll.objects.filter(
            student=student, enroll_activate=False, enroll_finished=False)
        enroll_finished = Enroll.objects.filter(
            student=student, enroll_finished=True)
        context['finished_enroll'] = enroll_finished.filter(Q(bill__is_paid=True)| Q(group__is_paid=False) | Q(paid_excluded=True))
        context['pending_enroll'] = Enroll.objects.filter(
            student=student, enroll_finished=True, group__is_paid=True, bill__is_paid=False)
    return render(request, 'enroll.html', context)


@login_required
def finish_enroll(request, pk):
    enroll = get_object_or_404(
        Enroll, pk=pk,
        enroll_activate=True,
        enroll_finished=False)
    enroll.enroll_finished = True
    group = enroll.group
    all_enrolls = Enroll.objects.filter(group=group, enroll_finished=True)
    if all_enrolls.count() < group.maximum:
        try:
            with transaction.atomic():
                enroll.save()
                schema = request.scheme+"://"
                send_email_from_template(
                    'email_enroll_success', [request.user.email],
                    {
                        "url": request.build_absolute_uri(reverse('enrollment')),
                        "group": enroll.group,
                        'domain': schema+request.get_host(),
                        'hours_to_pay': settings.HOURS_TO_PAY,
                    },
                    enqueued=False, user=None)
        except IntegrityError:
            messages.error(request, _('We have some problems with your enroll, try again'))
        if enroll.group.is_paid:
            messages.success(request, str(_('Enrollment success you have '))+str(settings.HOURS_TO_PAY)+str(_(' hours from now to complete the payment')) +' <a class="btn btn-primary" href="'+ str(reverse('bills'))+'">'+str(_('Pay Now')) +'</a>', 
                            extra_tags='safe')
        else:
            messages.success(request, str(_('Enrollment success.')))
    else:
        messages.error(request, str(_('The group is full and was not possible to enroll you.')))
    return redirect(reverse('enrollment'))
