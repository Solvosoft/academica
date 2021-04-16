from django.http import Http404
from django.template import Context, Template
from django.conf import settings
from django.utils.timezone import now
import re
import os
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
from django.core.files.base import File
import io
import logging

logger = logging.getLogger(__name__)


MONTHS_DICT = {
    'January': 'enero',
    'February': 'febrero',
    'March': 'marzo',
    'April': 'abril',
    'May': 'mayo',
    'June': 'junio',
    'July': 'julio',
    'August': 'agosto',
    'September': 'setiembre',
    'October': 'octubre',
    'November': 'noviembre',
    'December': 'diciembre'
}


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    uri = re.sub('../../../', "/", uri)
    sUrl = settings.STATIC_URL  # Typically /static/
    sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL  # Typically /media/
    mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def get_template_certificate_header(template):
    with open(settings.BASE_NOCODE_DIR / 'src/matricula/templates/Pdf/certificate_header.html', 'r') as arch:
        template = str(arch.read()).replace('CONTENT', template)
    return template


def get_context_certificate(enroll):
    today = now()
    context={


    }

def build_pdf_certificate(enroll):
    html = 'certificate.html'
    month = MONTHS_DICT['{:%B}'.format(now())]
    template = Template(get_template_certificate_header(enroll.group.certificate_template.template))
    date = str(now().day) + " de " + month + " del " + str(now().year)
    context = {"enrollment": enroll, 'certificate_date': date, }
    sourceHtml = template.render(Context(context))
    # FIXME the variable 'enqueued' == False, it must be false o we should change it to True?!
    resultFile = io.BytesIO()
    ''' 
        Be carefull to change it, it change the relative path of the images 
        saved using Tinymce editor to absolute path. Future updates in djgentelella
        Can make it crash, and it has to be changed to fit requirements.
    '''
    # sourceHtml = re.sub('../../../', settings.MY_PAYPAL_HOST+"/", sourceHtml)
    pisaStatus = pisa.CreatePDF(
        sourceHtml,  # the HTML to convert
        dest=resultFile,  # file handle to recieve result
        link_callback=link_callback)
    if pisaStatus.err:
        logger.error('We had some errors with code %s <pre>%s</pre>' % (pisaStatus.err, html))
        return
    resultFile.seek(0)
    file_name = f'certificado_{str(enroll.group)}_{str(enroll.student)}.pdf'
    enroll.pdf_certificate = File(resultFile, name=file_name)
    enroll.save()