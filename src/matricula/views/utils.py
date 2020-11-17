# encoding: utf-8

'''
Created on 16/5/2015

@author: luisza
'''
from datetime import datetime
from matricula.models import Period
from django.http.response import Http404
from django.utils.timezone import now, timedelta
from django.conf import settings


def get_active_period():
    period = Period.objects.filter(start_date__lte=datetime.now(),
                                   finish_date__gte=datetime.now())

    if period.exists():
        return period.last()
    raise Http404("No Active period")


def get_expire_date():
    return now() + timedelta(days=settings.TOKEN_CONFIRMATION_EXPIRE_DAYS)
