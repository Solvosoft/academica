import shutil
import subprocess
import tempfile
import uuid
import os
import re
import logging

from django.conf import settings
from django.utils.timezone import now
from django.contrib.staticfiles import finders
from django.core.files.base import File
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


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
    Convierte las URIs del HTML en rutas del sistema de archivos para que
    xhtml2pdf pueda leer imágenes y hojas de estilo.
    """
    uri = re.sub('../../../', "/", uri)
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, "", 1))
    elif uri.startswith(settings.STATIC_URL):
        relative = uri.replace(settings.STATIC_URL, "", 1)
        path = os.path.join(settings.STATIC_ROOT, relative)
        if not os.path.isfile(path):
            # En desarrollo no hay collectstatic: se busca en las apps.
            path = finders.find(relative) or path
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (settings.STATIC_URL, settings.MEDIA_URL)
        )
    return path


def render_pdf_response(template_name, context, filename):
    """Renderiza una plantilla HTML a PDF con xhtml2pdf y la devuelve como descarga."""
    html = get_template(template_name).render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if pisa_status.err:
        logger.error("Error generando el PDF %s: %s", filename, pisa_status.err)
        return HttpResponse("Error generando el PDF", status=500)
    return response


def build_pdf_certificate(enroll):
    template_file = settings.BASE_NOCODE_DIR / 'src/matricula/static/certificado_base.svg'
    uu = str(uuid.uuid4())
    file_name = 'certificado_'+uu+'.svg'
    file_name_pdf = f'certificado_'+uu+'.pdf'
    #copyfile(template_file, file_name)

    with open (template_file, 'r' ) as f:
        student_name = enroll.student.user.get_full_name()
        academica_hours = str(enroll.group.duration_hours) + " horas"
        academica_date = enroll.group.expedition_date
        if academica_date is None:
            academica_date = now().strftime("%Y-%m-%d")
        else:
            academica_date = str(academica_date)
        academica_course = str(enroll.group.course.name)
        content = f.read()
        small_course = ""
        medium_course = ""
        big_course = ""
        small_course2 = ""
        medium_course2 = ""
        big_course2 = ""
        if len(academica_course)<50:
            big_course = academica_course
        elif len(academica_course) <= 100:
            for i in range(50,0,-1):
                if academica_course[i] == " ":
                    big_course = academica_course[:i+1]
                    big_course2 = academica_course[i+1:]
                    break;
        elif len(academica_course)<=200:
            for i in range(100, 0, -1):
                if academica_course[i] == " ":
                    medium_course = academica_course[:i+1] 
                    medium_course2 = academica_course[i+1:]
                    break
        else:
            for i in range(150,0, -1):
                if academica_course[i] == " ":
                    small_course = academica_course[:i+1]
                    small_course2 = academica_course[i+1:]
                    break
                
        content = content.replace(
            '{{Nombre}}', student_name
        ).replace(
            '{{CursoGrande}}', big_course
        ).replace(
            '{{CursoMediano}}', medium_course
        ).replace(
            '{{CursoPequeno}}', small_course
        ).replace(
            '{{CursoGrande2}}', big_course2
        ).replace(
            '{{CursoMediano2}}', medium_course2
        ).replace(
            '{{CursoPequeno2}}', small_course2
        ).replace(
            '{{Cargahoraria}}', academica_hours
        ).replace(
            '{{Fecha}}', academica_date
        )
    tmpdir = tempfile.mkdtemp()
    with open(tmpdir+'/'+file_name, 'w') as tmfile:
        tmfile.write(content)
    subprocess.run("rsvg-convert -f pdf -o %s %s"%(
            tmpdir + '/' + file_name_pdf,
            tmpdir + '/' + file_name
    ), shell=True)
    with open(tmpdir + '/' + file_name_pdf, 'rb') as f:
        enroll.pdf_certificate = File(f, name=file_name_pdf)
        enroll.save()
        f.close()
    shutil.rmtree(tmpdir)
