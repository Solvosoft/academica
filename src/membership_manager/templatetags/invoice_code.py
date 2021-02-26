import textwrap
from django import template
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
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
    w = 50
    d = [text[i:i + w] for i in range(0, len(text), w)]
    dev = "<br>".join(d)
    return mark_safe(dev)

@register.simple_tag
def limit_long_text_code(text):
    w = 50
    lines = textwrap.wrap(text, w)
    dev = "<br>".join(lines)
    return mark_safe(dev)

@register.simple_tag
def month_by_number(text):
    months={
        '1': 'Enero',
        '2': 'Febrero',
        '3': 'Marzo',
        '4': 'Abril',
        '5': 'Mayo',
        '6': 'Junio',
        '7': 'Julio',
        '8': 'Agosto',
        '9': 'Septiembre',
        '10': 'Octubre',
        '11': 'Noviembre',
        '12': 'Diciembre'


    }
    return months[str(text)]

@register.simple_tag(takes_context=True)
def next_url(context):
    url = reverse('invoice-list')+'?year='+str(context['current_year'])+context['params']
    return urlsafe_base64_encode(url.encode())