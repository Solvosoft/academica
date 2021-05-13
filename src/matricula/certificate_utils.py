import shutil
import subprocess
import tempfile
import uuid
import os
import re
import logging

from django.conf import settings
from django.utils.timezone import now
from django.core.files.base import File


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
    template_file = settings.BASE_NOCODE_DIR / 'src/matricula/static/certificado_base.svg'
    uu = str(uuid.uuid4())
    file_name = 'certificado_'+uu+'.svg'
    file_name_pdf = f'certificado_'+uu+'.pdf'
    #copyfile(template_file, file_name)

    with open (template_file, 'r' ) as f:
        student_name = enroll.student.user.get_full_name()
        upo_hours = str(enroll.group.duration_hours) + " horas"
        upo_date = enroll.group.expedition_date
        if upo_date is None:
            upo_date = now().strftime("%Y-%m-%d")
        else:
            upo_date = str(upo_date)
        upo_course = str(enroll.group.course.name)
        content = f.read()
        small_course = ""
        medium_course = ""
        big_course = ""
        small_course2 = ""
        medium_course2 = ""
        big_course2 = ""
        if len(upo_course)<50:
            big_course = upo_course
        elif len(upo_course) <= 100:
            for i in range(50,0,-1):
                if upo_course[i] == " ":
                    big_course = upo_course[:i+1]
                    big_course2 = upo_course[i+1:]
                    break;
        elif len(upo_course)<=200:
            for i in range(100, 0, -1):
                if upo_course[i] == " ":
                    medium_course = upo_course[:i+1] 
                    medium_course2 = upo_course[i+1:]
                    break
        else:
            for i in range(150,0, -1):
                if upo_course[i] == " ":
                    small_course = upo_course[:i+1]
                    small_course2 = upo_course[i+1:]
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
            '{{Cargahoraria}}', upo_hours
        ).replace(
            '{{Fecha}}', upo_date
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
