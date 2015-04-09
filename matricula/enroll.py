'''
Created on 8/4/2015

@author: luisza
'''
from django_ajax.decorators import ajax
from django.shortcuts import get_object_or_404, render, redirect
from matricula.models import Group, Enroll
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils import timezone



@ajax
@login_required
def enrollme(request, pk):
    group = get_object_or_404(Group, pk=pk)
    list_enroll = Enroll.objects.filter(group=group, student=request.user)
    if not list_enroll.exists():
        Enroll.objects.create(group=group,
                              student=request.user)
        return { "inner-fragments": {"#count_" + str(group.pk): group.enroll_set.count(),
                                "#group_message": '<div class="alert alert-success" role="alert">Enrollment success...</div>'
                                },
            }

    return { "inner-fragments": {"#count_" + str(group.pk): group.enroll_set.count(),
                                "#group_message": '<div class="alert alert-info" role="alert">You are alredy enrollment ...</div>'
                                },
            }


@login_required
def list_enroll(request):
    list_enroll = Enroll.objects.filter(student=request.user, enroll_activate=True, enroll_finished=False,
      group__enroll_start__lte=timezone.now(),
      group__enroll_finish__gte=timezone.now())
    finished_enroll = Enroll.objects.filter(student=request.user, enroll_finished=True) 
    return render(request, 'enroll.html', {'list_enroll': list_enroll,
                                           'finished_enroll': finished_enroll}
                  )


@login_required
def finish_enroll(request, pk):
    enroll = get_object_or_404(Enroll, pk=pk)
    enroll.enroll_finished = True
    enroll.save()
    return redirect(reverse('enrollment'))
