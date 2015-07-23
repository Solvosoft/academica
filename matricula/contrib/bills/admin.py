# encoding: utf-8

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
# 
from matricula.menues import add_main_menu
from matricula.contrib.bills.models import Bill, Colon_Exchange

admin.site.register(Colon_Exchange)
admin.site.register(Bill)

add_main_menu((_("Bills"), 'bills', True, 3, True))

from matricula.admin import admin_site

admin_site.register(Bill)
admin_site.register(Colon_Exchange)