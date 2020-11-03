from django import template


register = template.Library()
@register.filter(name='index')
def index(array, index):
    dev = array[index]
    return dev