# encoding: utf-8
from django.contrib import admin
from django.core.mail import send_mail
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from matricula.menues import add_main_menu
from django.contrib import messages

from matricula.contrib.bills.card_payments import refresh_card_payment
from matricula.contrib.bills.models import Bill, BankBill, SinpeMovilBill, CardPayment
from matricula.contrib.bills.webcheckout import WebCheckoutError


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


@admin.action(description=_("Check status in the payment service"))
def refresh_status(modeladmin, request, queryset):
    for card_payment in queryset:
        try:
            refresh_card_payment(card_payment)
        except WebCheckoutError as exc:
            messages.error(request, "%s: %s" % (card_payment.order_id, exc))


@admin.register(CardPayment)
class CardPaymentAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'bill', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('order_id', 'bill__student__user__email', 'authorization_code')
    readonly_fields = [field.name for field in CardPayment._meta.fields]
    actions = [refresh_status]

    def has_add_permission(self, request):
        return False
add_main_menu((_("Bills"), 'bills', True, 3, True))
