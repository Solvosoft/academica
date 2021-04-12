'''
Created on 17 jul. 2017

@author: luis
'''

# coding: utf-8

import os

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


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
                sUrl = settings.STATIC_URL        # Typically /static/
                sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
                mUrl = settings.MEDIA_URL         # Typically /media/
                mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

                if uri.startswith(mUrl):
                        path = os.path.join(mRoot, uri.replace(mUrl, ""))
                elif uri.startswith(sUrl):
                        path = os.path.join(sRoot, uri.replace(sUrl, ""))
                else:
                        return uri

        # make sure that file exists
        if not os.path.isfile(path):
                raise Exception('media URI must start with %s or %s' % (sUrl, mUrl) )
        return path


def render_pdf(request, name, template_path, context={}):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % (name,)

    template = get_template(template_path)
    html = template.render(context)
    pisaStatus = pisa.CreatePDF(
        str(html).encode('ISO-8859-15'), dest=response, link_callback=link_callback)
    if pisaStatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisaStatus.err,
                                                                               html))
    return response


def action_pdf_certificaciones(modeladmin, request, queryset):

    return render_pdf(request, "certificados.pdf", 'matricula/certificaciones.html', context={
        'object_list': queryset,
        'event': current_event,
        'event_logo': logo

    })