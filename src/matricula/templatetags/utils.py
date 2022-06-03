import urllib

from django import template
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe

from matricula.models import Enroll, Group

register = template.Library()
@register.filter(name='index')
def index(array, index):
    dev = array[index]
    return dev

# settings value
@register.simple_tag
def is_admin(group_name, name):
    name_settings = getattr(settings, name, "")
    if name_settings == group_name:
        return mark_safe("<span class='badge'>"+_("Administrator")+"</span>")
    return ''

@register.filter
def is_open(course):
    result = False
    groups = course.group_set.filter(is_open=True)
    if groups.exists():
        result = groups
    return result

@register.simple_tag
def can_enroll(group, user):
    try:
        student = user.student
    except:
        return False
    if group.flow in (Group.NORMAL, Group.AUTO_PREENROLL):
        return Enroll.objects.filter(
            group=group, student=student, enroll_activate=True,enroll_finished=False).exists()
    else:
        return not Enroll.objects.filter(
            group=group, student=student, enroll_finished=True).exists()


@register.filter
def group_state(state):
    result = 'Abierto'
    if not state:
        result = 'Cerrado'
    return result

@register.filter
def as_number_percent(studentscore):
    score = 0
    try:
        score = int(studentscore)
    except ValueError as e:
        score = 0
    if score < 0:
        score = 0
    if score > 100:
        score= 100

    return score

@register.simple_tag(takes_context=True)
def reverse_login(context):
    return reverse('login') +'?next=' + urllib.parse.quote_plus(context['request'].path)


@register.simple_tag(takes_context=True)
def reverse_register(context):
    return reverse('create_user_academy') +'?next=' + urllib.parse.quote_plus(context['request'].path)
