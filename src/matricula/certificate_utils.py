import shutil
import subprocess
import tempfile
import uuid

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
import re
from shutil import copyfile
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
        len_name = 393.49072 - len(student_name)*6
        upo_hours = str(enroll.group.duration_hours) + " horas"
        len_hours = 394.11533 - len(upo_hours)*6
        upo_date = enroll.group.expedition_date
        if upo_date is None:
            upo_date = now().strftime("%Y-%m-%d")
        else:
            upo_date = str(upo_date)
        len_date = 393.81189 - len(upo_date)*6
        upo_course = str(enroll.group.course.name)
        extra_course_name = ""
        course_name = upo_course
        if len(upo_course) > 50:
            for i in range(50, 0, -1):
                if upo_course[i] == " ":
                    course_name = upo_course[:i+1]
                    len_course = 393.46133 - len(course_name)*6
                    extra_course_name = upo_course[i+1:]
                    if len(extra_course_name) > 50:
                        extra_course_name = extra_course_name[:50]
                    break;
        else:
            len_course = 393.46133 - len(upo_course)*6
        content = f.read()
        content = content.replace(
            '{{Nombre}}', student_name
        ).replace(
            '{{Curso}}', course_name
        ).replace(
            '{{Cargahoraria}}', upo_hours
        ).replace(
            "{{ExtraCurso}}", extra_course_name
        ).replace(
            '{{Fecha}}', upo_date
        ).replace(
            "id=\"tspan4680-5\" x=\"394.11533\"", f"id=\"tspan4680-5\" x=\"{len_hours}\""
        ).replace(
            "id=\"tspan4680\" x=\"393.49072\"", f"id=\"tspan4680\" x=\"{len_name}\""
        ).replace(
            "id=\"tspan4680-1\" x=\"393.46133\"", f"id=\"tspan4680-1\" x=\"{len_course}\""
        ).replace(
            "id=\"tspan4680-9\" x=\"393.81189\"", f"id=\"tspan4680-9\" x=\"{len_date}\""
        )
        if len(extra_course_name)>0:
            len_extra_course = 394.10159 - len(extra_course_name)*6
            content = content.replace(
                "id=\"tspan4680-1-8\" x=\"394.10159\"", f"id=\"tspan4680-1-8\" x=\"{len_extra_course}\""
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
