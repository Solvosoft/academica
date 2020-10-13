from django import template

from membership_manager.models import PAYMENT

register = template.Library()

@register.simple_tag()
def get_payment_method(payment_method):
    for key, value in PAYMENT:
        if key == payment_method:
            return value