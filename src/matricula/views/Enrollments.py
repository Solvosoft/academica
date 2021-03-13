# encoding: utf-8

'''
Created on 17/5/2015

@author: luisza
'''

from django_ajax.decorators import ajax
from django.shortcuts import get_object_or_404, render, redirect
from matricula.models import Group, Enroll
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError, transaction
from async_notifications.utils import send_email_from_template
from django.db.models import Q
from django.contrib import messages


@ajax
@login_required
def enrollme(request, pk):
    group = get_object_or_404(Group, pk=pk)
    student = request.user.student
    list_enroll = Enroll.objects.filter(group=group, student=student)
    if not list_enroll.exists():
        try:
            template = 'email_enroll_success'
            schema = request.scheme+"://"
            with transaction.atomic():
                enroll = Enroll.objects.create(group=group, student=student)
                if group.flow == group.AUTO_PREENROLL:
                    enroll.enroll_activate = True
                    enroll.save()
                    template = 'email_preenroll_success'
                    send_email_from_template(
                        template, [enroll.student.user.email],
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
                elif group.flow == group.AUTO_ENROLL:
                    enroll.enroll_activate = True
                    enroll.enroll_finished = True
                    enroll.save()
                    send_email_from_template(
                        template, [enroll.student.user.email],
                        {
                            "url": request.build_absolute_uri(reverse('enrollment')),
                            "group": group,
                            'domain': schema+request.get_host(),
                        },
                        enqueued=True, user=None)
                    return {
                        "inner-fragments": {
                            "#count_" + str(group.pk): group.enroll_set.count(),
                            "#group_message": '<div class="alert alert-success" role="alert">' + str(_('Enrollment success')) + '</div>'
                        },
                    }
        except IntegrityError:
            return { "inner-fragments": {"#count_" + str(group.pk): group.enroll_set.count(),
                                        "#group_message": '<div class="alert alert-info" role="alert">' + str(_('We have some problems with your enroll, try again')) + ' </div>'
                                        },
                    }
    message = _('You are already pre-enrolled')
    if list_enroll.first().enroll_finished:
        message = _('You are already enrolled')
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
        list_enr = list_enr.filter(
            Q(
                group__enroll_start__lte=timezone.now(),
                group__enroll_finish__gte=timezone.now()
            ) | 
            Q(
                group__pre_enroll_start__lte=timezone.now(),
                group__pre_enroll_finish__gte=timezone.now()
            )
        )
        context['list_enroll'] = list_enr
        list_pre = Enroll.objects.filter(
            student=student, enroll_activate=False, enroll_finished=False)
        list_pre = list_pre.filter(
            Q(
                group__enroll_start__lte=timezone.now(),
                group__enroll_finish__gte=timezone.now()
            ) | 
            Q(
                group__pre_enroll_start__lte=timezone.now(),
                group__pre_enroll_finish__gte=timezone.now()
            )
        )
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
    except IntegrityError:
        return { "inner-fragments": {"#group_message": '<div class="alert alert-info" role="alert">' + str(_('We have some problems with your enroll, try again')) + ' </div>'
                                    },
                }
    messages.success(request, _("Enrollment successfully"))
    return redirect(reverse('enrollment'))
