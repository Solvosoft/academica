from django import template

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