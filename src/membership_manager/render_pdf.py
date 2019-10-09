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
        sourceHtml,         # the HTML to convert
        dest=resultFile,    # file handle to recieve result
        link_callback=link_callback)
    resultFile.seek(0)

    invoice.pdf_invoice = File(resultFile, name="invoice.pdf")
    invoice.status = 'paid'
    invoice.save()


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
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path