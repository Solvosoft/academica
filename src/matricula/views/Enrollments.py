# encoding: utf-8

'''
Created on 17/5/2015

@author: luisza
'''

from django_ajax.decorators import ajax
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.contrib import messages
from django.conf import settings

from async_notifications.utils import send_email_from_template

from matricula.models import Group, Enroll


@ajax
@login_required
def enrollme(request, pk):
    group = get_object_or_404(Group, pk=pk)
    student = request.user.student
    list_enroll = Enroll.objects.filter(group=group, student=student)
    schema = request.scheme+"://"
    if not list_enroll.exists():
        try:
            template = 'email_enroll_success'
            with transaction.atomic():
                enroll = Enroll.objects.create(group=group, student=student)
                if group.in_enrollment and group.flow == group.AUTO_ENROLL or group.in_enrollment and group.flow == group.AUTO_PREENROLL:
                    enroll.enroll_activate = True
                    enroll.enroll_finished = True
                    enroll.save()
                    send_email_from_template(
                        template, [request.user.email],
                        {
                            "url": request.build_absolute_uri(reverse('enrollment')),
                            "group": group,
                            'domain': schema+request.get_host(),
                        },
                        enqueued=True, user=None)
                    return {
                        "inner-fragments": {
                            "#count_" + str(group.pk): group.enroll_set.count(),
                            "#group_message": '<div class="alert alert-success" role="alert">' + str(_('Enrollment success you have 20 minutes from now to complete the payment')) +' <a class="btn btn-primary" href="'+ reverse('bills')+'">'+str(_('Pay Now')) +'</a>'+'</div>'
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
                        enqueued=True, user=None)
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
            if enroll.enroll_activate and not enroll.enroll_finished:
                enroll.enroll_finished = True
                enroll.save()
                send_email_from_template(
                    'email_enroll_success', [request.user.email],
                    {
                        "url": request.build_absolute_uri(reverse('enrollment')),
                        "group": group,
                        'domain': schema+request.get_host(),
                    },
                    enqueued=True, user=None)
                message = _('Enrollment success')
            elif enroll.enroll_activate and enroll.enroll_finished:
                message = _('You are already enrolled')
            else:
                message = _('You are already pre-enrolled')
        else:
            message = _('You are already pre-enrolled')
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
        list_enr = Enroll.objects.filter(
            student=student, enroll_activate=True, enroll_finished=False)
        context['list_enroll'] = list_enr
        list_pre = Enroll.objects.filter(
            student=student, enroll_activate=False, enroll_finished=False)
        context['list_pre'] = list_pre
        context['finished_enroll'] = Enroll.objects.filter(student=student, enroll_finished=True).order_by("-enroll_date")
    return render(request, 'enroll.html', context)


@login_required
def finish_enroll(request, pk):
    enroll = get_object_or_404(
        Enroll, pk=pk,
        enroll_activate=True,
        enroll_finished=False)
    enroll.enroll_finished = True

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
                },
                enqueued=True, user=None)
    except IntegrityError:
        messages.error(request, _('We have some problems with your enroll, try again'))
    messages.success(request, _("Enrollment successfully"))
    return redirect(reverse('enrollment'))
