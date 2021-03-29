# encoding: utf-8

'''
Created on 16/5/2015

@author: luisza
'''
from datetime import datetime
from matricula.models import Period
from django.utils.timezone import now, timedelta
from django.conf import settings

from matricula.models import Student


def get_active_period():
    period = Period.objects.filter(start_date__lte=datetime.now(),
                                   finish_date__gte=datetime.now())
    return period.all()

def get_expire_date():
    return now() + timedelta(days=settings.TOKEN_CONFIRMATION_EXPIRE_DAYS)

def checking_user(user):
    return  Student.objects.filter(user=user).exists() or \
            user.groups.filter(name=settings.ADMIN_GROUP_NAME).exists()