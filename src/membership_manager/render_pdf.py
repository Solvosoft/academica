from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io
import os
from django.conf import settings
from django.core.files.base import File


def generate_invoice(membership, invoice):
    sourceHtml = render_to_string('invoice.html', context={
        'invoice': invoice,
        'membership': membership
    })
    resultFile = io.BytesIO()
    pisaStatus = pisa.CreatePDF(
        sourceHtml,  # the HTML to convert
        dest=resultFile,  # file handle to recieve result
        link_callback=link_callback)
    resultFile.seek(0)

    invoice.pdf_invoice = File(resultFile, name="invoice.pdf")
    invoice.status = 'paid'
    invoice.save()

    context = [
        ('subject', 'Pago de membresía - Código Sur'),
        ('message', 'Estimado cliente:\nPor este medio se le informa que el pago de su factura ha sido efectuado. '
                    'Los detalles son aclarados en su factura digital la cual se adjunta acontinuación.'
                    '\n\nGracias por seguir con nosotros.\nCódigo Sur'),
    ]

    code = str(invoice.pdf_invoice.name[invoice.pdf_invoice.name.rfind('/') + 1: invoice.pdf_invoice.name.rfind('.')])

    update_template_context(code, 'pay_email.html', 'Pago de membresía - Código Sur', context)

    send_email_from_template(code, [membership.contact.email],
                             context={},
                             enqueued=False,  # ask about this! Docu says: enqueued if False send the email
                                              # immediately else enqueued to be sended when send email task run.
                             user=None,
                             upfile=invoice.pdf_invoice.url)


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri

    # make sure that file exists
    if not os.path.isfile(path):
        print(path)
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path
