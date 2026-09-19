"""
Reemplazo mínimo de djangoajax (``@ajax``).

Las vistas decoradas devuelven un diccionario (o una respuesta de Django) y el
decorador lo envuelve en el mismo formato que usaba djangoajax, que es el que
consume ``static/js/ajax_fragments.js``::

    {"status": 200, "statusText": "OK", "content": {...}}

Un ``redirect`` se transmite como ``{"status": 302, "content": "<url>"}``.
"""
import logging
from decimal import Decimal
from datetime import date
from functools import wraps
from http import HTTPStatus

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.http.response import HttpResponseRedirectBase
from django.template.response import TemplateResponse
from django.utils.encoding import force_str

logger = logging.getLogger(__name__)


def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


class AjaxJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            return force_str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return force_str(obj)
        try:
            return list(iter(obj))
        except TypeError:
            return super().default(obj)


def _status_text(code):
    try:
        return HTTPStatus(code).phrase.upper()
    except ValueError:
        return 'UNKNOWN STATUS CODE'


def render_to_json(response, request=None):
    if isinstance(response, HttpResponseRedirectBase):
        status, content = response.status_code, response['Location']
    elif isinstance(response, TemplateResponse):
        status, content = response.status_code, response.rendered_content
    elif isinstance(response, HttpResponse):
        status, content = response.status_code, force_str(response.content)
    elif isinstance(response, Http404):
        status, content = 404, force_str(response)
    elif isinstance(response, Exception):
        logger.exception(str(response), extra={'request': request})
        status = 500
        content = str(response) if settings.DEBUG else \
            'An error occured while processing an AJAX request.'
    else:
        status, content = 200, response
    return JsonResponse({'status': status, 'statusText': _status_text(status),
                         'content': content}, encoder=AjaxJSONEncoder, safe=False)


def ajax(function=None, mandatory=True):
    """Decorador compatible con ``django_ajax.decorators.ajax``."""
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if not is_ajax(request):
                if mandatory:
                    return HttpResponseBadRequest()
                return func(request, *args, **kwargs)
            try:
                return render_to_json(func(request, *args, **kwargs), request)
            except Exception as exception:
                return render_to_json(exception, request)
        return inner

    if function:
        return decorator(function)
    return decorator
