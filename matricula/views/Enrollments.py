# encoding: utf-8

'''
Created on 17/5/2015

@author: luisza
'''

from django_ajax.decorators import ajax
from django.shortcuts import get_object_or_404, render, redirect
from matricula.models import Group, Enroll
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError, transaction

@ajax
@login_required
def enrollme(request, pk):
    group = get_object_or_404(Group, pk=pk)
    list_enroll = Enroll.objects.filter(group=group, student=request.user)
    if not list_enroll.exists():
        try:
            with transaction.atomic():
                enroll = Enroll.objects.create(group=group, student=request.user)
            if group.flow == group.AUTO_PREENROLL:
                enroll.enroll_activate = True
                enroll.save()
            elif group.flow == group.AUTO_ENROLL:
                enroll.enroll_activate = True
                enroll.enroll_finished = True
                enroll.save()
        except IntegrityError:
            return { "inner-fragments": {"#count_" + str(group.pk): group.enroll_set.count(),
                                        "#group_message": '<div class="alert alert-info" role="alert">' + str(_('We have some problems with your enroll, try again')) + ' </div>'
                                        },
                    }

        return { "inner-fragments": {"#count_" + str(group.pk): group.enroll_set.count(),
                                "#group_message": '<div class="alert alert-success" role="alert">' + str(_('Enrollment success')) + '</div>'
                                },
            }

    return { "inner-fragments": {"#count_" + str(group.pk): group.enroll_set.count(),
                                "#group_message": '<div class="alert alert-info" role="alert">' + str(_('You are already enrolled')) + '</div>'
                                },
            }


@login_required
def list_enroll(request):
    list_enroll = Enroll.objects.filter(student=request.user, enroll_activate=True, enroll_finished=False,
      group__enroll_start__lte=timezone.now(),
      group__enroll_finish__gte=timezone.now()).order_by("-enroll_date")

    finished_enroll = Enroll.objects.filter(student=request.user, enroll_finished=True).order_by("-enroll_date")

    return render(request, 'enroll.html', {'list_enroll': list_enroll,
                                           'finished_enroll': finished_enroll}
                  )


@login_required
def finish_enroll(request, pk):
    enroll = get_object_or_404(Enroll, pk=pk)
    enroll.enroll_finished = True

    try:
        with transaction.atomic():
            enroll.save()
    except IntegrityError:
        return { "inner-fragments": {"#group_message": '<div class="alert alert-info" role="alert">' + str(_('We have some problems with your enroll, try again')) + ' </div>'
                                    },
                }
    return redirect(reverse('enrollment'))
