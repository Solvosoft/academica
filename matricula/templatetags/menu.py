'''
Created on 18/5/2015

@author: luisza
'''
from matricula import menues

from django.utils.safestring import mark_safe
from django import template
from django.core.urlresolvers import reverse
register = template.Library()


@register.simple_tag
def show_menu(user_auth):
    if not menues.menu_sort:
        menues.main_menu.sort(key=lambda menu: menu[3], reverse=False)
        menues.menu_sort = True

    dev = '<ul class="nav navbar-nav">'
    for menu in menues.main_menu:
        if not menu[2] or user_auth:
            link = reverse(menu[1]) if menu[4] else menu[1]
            dev += '<li role="presentation" ><a href="%s"> %s</a></li>' % (
                        link, menu[0])
    dev += "</ul>"
    return mark_safe(dev)
