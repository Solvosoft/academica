# encoding: utf-8

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
# 
from matricula.menues import add_main_menu
from matricula.contrib.bills.models import Bill


admin.site.register(Bill)

add_main_menu((_("Bills"), 'bills', True, 3, True))
