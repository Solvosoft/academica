from django import template
from django.conf import settings

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
        return "<span class='badge'>"+_("Administrator")+"</span>"
    return ''

@register.filter
def is_open(course):
    result = False
    groups = course.group_set.filter(is_open=True)
    if groups.exists():
        result = groups
    return result

@register.filter
def group_state(state):
    result = 'Abierto'
    if not state:
        result = 'Cerrado'
    return result
