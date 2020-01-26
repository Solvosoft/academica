from django import template
from django.utils.safestring import mark_safe

from membership_manager.utils import stringcode_generator

register = template.Library()

@register.simple_tag
def new_invoice_code(invoice):
    invoice_pk = invoice.id
    if invoice.code:
        return invoice.code

    string_code = stringcode_generator()
    new_invoice_code = f'%s-%s' % (string_code,str(invoice_pk).rjust(6, "0"))
    invoice.code = new_invoice_code
    invoice.save()
    return new_invoice_code

@register.simple_tag
def limit_text_code(text):
    dev = text
    w = 50
    d = [text[i:i + w] for i in range(0, len(text), w)]
    dev = "<br>".join(d)
    print(dev)
    return mark_safe(dev)