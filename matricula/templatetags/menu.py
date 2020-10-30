'''
Created on 18/5/2015

@author: luisza
'''

from collections import OrderedDict
from django.utils.safestring import mark_safe
from django import template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from matricula.models import MenuItem

register = template.Library()


def insert_in_item(item, menu):
    dev = False
    if item['obj'].pk == menu.parent.pk:
        item['children'].append({'obj': menu,
                                 'children': []})
        dev = True
    else:
        for child in item['children']:
            dev = insert_in_item(child, menu)
            if dev:
                break
    return dev


def get_menu_items(user_auth, is_student):
    # FIXME do cache for this 
    menues = MenuItem.objects.filter(publicated=True).order_by('order')
    no_root = []
    dic_menu = OrderedDict()
    for menu in menues:
        if not user_auth and menu.require_authentication:
            continue

        if menu.parent is None:
            dic_menu[menu.pk] = {'obj': menu,
                                 'children': []
                                 }
        else:
            if menu.parent.pk in dic_menu:
                dic_menu[menu.parent.pk]['children'].append({'obj': menu,
                                                 'children': []
                                                 })
            else:
                dev = False
                for x in dic_menu:
                    dev = insert_in_item(dic_menu[x], menu)
                    if dev:
                        break
                if not dev:
                    no_root.append(menu)

    while no_root:
            menu = no_root.pop(0)
            dev = False
            for x in dic_menu:
                dev = insert_in_item(dic_menu[x], menu)
                if dev:
                    break
            if not dev:
                no_root.append(menu)

    return dic_menu


def get_ref_and_ref_display(request, menu):
    ref = "/"
    ref_display = "I am wrong"
    if menu.type == 0:
        ref = reverse(menu.name)
        ref_display = _(menu.description)
    elif menu.type == 1:
        ref = reverse("academica_pages", args=(menu.name,))
        ref_display = menu.get_title_menu(request)
    elif menu.type == 2:
        ref = reverse(menu.name, args=(menu.description,))
        ref_display = menu.get_title_menu(request)

    return ref, ref_display


def print_menu_item(request, menues, is_list=False):
    dev = ""
    if is_list:
        items_menu = zip(range(len(menues)), menues)
    else:
        items_menu = menues.items()

    for key, menu in items_menu:
        ref, ref_display = get_ref_and_ref_display(request, menu['obj'])
        if not menu['children']:
            dev += '<li><a href="%s"> %s</a>' % (ref, strip_tags(ref_display))
        if menu['children']:
            dev += '<li><a>'+ ref_display +'<span class="fa fa-chevron-down"></span></a>'+\
            '<ul class="nav child_menu">' + print_menu_item(request, menu['children'], True) + "</ul>"
        dev += '</li>'

    return dev


@register.simple_tag(takes_context=True)
def show_menu(context, user_auth, is_student):
    menues = get_menu_items(user_auth, is_student)
    dev = '<ul><li class="nav child_menu">' + print_menu_item(context['request'], menues) + "</li></ul>"
    dev = print_menu_item(context['request'], menues)
    return mark_safe(dev)
