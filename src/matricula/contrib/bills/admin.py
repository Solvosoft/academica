# encoding: utf-8
from django.contrib import admin
from django.core.mail import send_mail
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from matricula.admin import admin_site
from matricula.menues import add_main_menu
from matricula.contrib.bills.models import Bill, BankBill, SinpeMovilBill


def approve_payment(modeladmin, request, queryset):
    for pay in queryset:
        bill=pay.bill
        bill.is_paid=True
        bill.paid_date =  now()
        bill.transaction_id = "%s %s"%(pay.__class__.__name__, pay.pk)
        bill.save()
        pay.verified=True
        pay.save()
        email = bill.student.user.email
        send_mail("Tu pago ha sido aplicado",
            "Hola, hemos procesado su pago para el grupo %s, tu matricula ya fue activada y lo esperamos en el curso"%(pay.group_name),
            None,
            [email]

        )

class PaymentAdmin(admin.ModelAdmin):
    actions = [approve_payment]
    list_filter = ['verified', 'bill__student']

admin.site.register(BankBill, PaymentAdmin)
admin.site.register(SinpeMovilBill, PaymentAdmin)
admin.site.register(Bill)
add_main_menu((_("Bills"), 'bills', True, 3, True))
admin_site.register(Bill)
