# encoding: utf-8

'''
Created on 16/5/2015

@author: luisza
'''
from datetime import datetime
from matricula.models import Period
from django.http.response import Http404


def get_active_period():
    period = Period.objects.filter(start_date__lte=datetime.now(),
                                   finish_date__gte=datetime.now())

    if period.exists():
        return period.last()
    raise Http404("No Active period")
