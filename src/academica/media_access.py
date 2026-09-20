"""
Acceso controlado a los archivos privados de ``MEDIA_ROOT``.

nginx sirve `/media/` directo desde el disco, que para las imagenes de cursos y
categorias esta bien: son publicas. Pero ahi caian tambien dos cosas que NO lo
son, y bastaba con tener la URL para bajarlas sin sesion:

  * ``certificates/`` -- el certificado de cada estudiante;
  * ``bank/``         -- los comprobantes de deposito (nombre del depositante,
    cuenta, monto y, en la practica, una foto del comprobante).

Estas dos rutas pasan ahora por Django, que decide, y el archivo lo sigue
sirviendo nginx con ``X-Accel-Redirect``: la aplicacion no lee el archivo ni lo
mete en memoria, solo dice cual.

Quien puede:
  * el personal (superusuario, grupo de administracion, o permiso de ver
    matriculas -- que es lo que tienen los profesores en los listados);
  * el dueno: el estudiante de esa matricula, o el de la factura del deposito.
"""
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.views.static import serve

# Solo estas rutas llegan aqui (ver academica/urls.py). Cualquier otra la sirve
# nginx directo, como antes.
PROTECTED_PREFIXES = ("certificates/", "bank/")


def _is_staff(user):
    return (
        user.is_superuser
        or user.groups.filter(name=settings.ADMIN_GROUP_NAME).exists()
        # Los profesores lo tienen: es el permiso con el que ven el listado de
        # estudiantes de su grupo, donde esta el enlace al certificado.
        or user.has_perm("matricula.view_enroll")
    )


def _owns(user, path):
    from matricula.contrib.bills.models import BankBill
    from matricula.models import Enroll

    if path.startswith("certificates/"):
        return Enroll.objects.filter(pdf_certificate=path,
                                     student__user=user).exists()
    if path.startswith("bank/"):
        return BankBill.objects.filter(payment_document=path,
                                       bill__student__user=user).exists()
    return False


def media_access(request, path):
    if not request.user.is_authenticated:
        # Redirigir al login y no un 403 seco: el caso normal es alguien que
        # abre el enlace de su certificado con la sesion vencida.
        return redirect_to_login(request.get_full_path())

    if not path.startswith(PROTECTED_PREFIXES):
        # Defensa en profundidad: si alguien enruta aqui otra cosa, no se
        # convierte en un servidor de archivos abierto para quien tenga sesion.
        raise PermissionDenied

    if not (_is_staff(request.user) or _owns(request.user, path)):
        raise PermissionDenied

    if settings.DEBUG:
        # En desarrollo no hay nginx que atienda el X-Accel-Redirect.
        return serve(request, path, document_root=settings.MEDIA_ROOT)

    response = HttpResponse()
    # La ruta la resuelve el `location /_protected/` de deploy/nginx.conf, que
    # es `internal`: no se puede pedir desde fuera.
    response["X-Accel-Redirect"] = "/_protected/%s" % path
    # Que lo decida nginx por la extension; con el vacio no manda Content-Type.
    del response["Content-Type"]
    return response
