import io
import os

from django.http import HttpResponse

from async_notifications.utils import send_email_from_template
from django.conf import settings
from django.core.files.base import File
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders

from membership_manager.utils import get_emails


def build_pdf_invoice(membership, invoice):
    html= 'invoice.html'
    sourceHtml = render_to_string('invoice.html', context={
        'invoice': invoice,
        'membership': membership
    })
    #FIXME the variable 'enqueued' == False, it must be false o we should change it to True?!
    resultFile = io.BytesIO()

    pisaStatus = pisa.CreatePDF(
        sourceHtml,  # the HTML to convert
        dest=resultFile,  # file handle to recieve result
        link_callback=link_callback)
    if pisaStatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisaStatus.err,
                                                                               html))
    resultFile.seek(0)
    file_name = f'factura_{invoice.pk}_{membership.name}.pdf'
    invoice.pdf_invoice = File(resultFile, name=file_name)
    invoice.save()

def generate_invoice(membership, invoice, email_template='pay_mail',
                     enqueued=True, send_email=True, buildpdf=True):
    if buildpdf:
        if invoice.pdf_invoice:
            invoice.pdf_invoice.delete(False)
        build_pdf_invoice(membership, invoice)
    if send_email:
        emails = get_emails(membership)
        send_email_from_template(email_template, emails,
                             context={
                                 'invoice': invoice,
                                 'membership': membership
                             },
                             enqueued=enqueued,
                             user=None,
                             upfile=invoice.pdf_invoice)

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path=result[0]
    else:
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
