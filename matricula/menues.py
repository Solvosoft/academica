# encoding: utf-8
'''
Created on 18/5/2015

@author: luisza
'''
from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

menu_sort = False
main_menu = [
             (_("Courses"), 'courses', False, 0, True),
             (_("Enrollment"), 'enrollment', True, 2, True),

             ]


def add_main_menu(item):
    """
    Permite agregar elementos al menú

    Puede ser una lista de tuplas o una tupla con el siguiente formato

        (texto de despliegue, link, es autenticado, orden, use reverse)

    por ejemplo

        ("Factura", "/bills/", True, 3, False)

    también es válido

        [ (..), ("Curso", "courses", False, 0, True), (...)]

    """

    global main_menu
    if type(item) == list:
        main_menu += item
    else:
        main_menu.append(item)
