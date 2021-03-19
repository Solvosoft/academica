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
