import sys

from django import template

register = template.Library()

@register.simple_tag
def get_version():
    return sys.modules['matricula'].__version__