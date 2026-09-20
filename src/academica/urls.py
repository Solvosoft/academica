from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from djgentelella.urls import urlpatterns as djgentelellaurls

from academica.health import health
from academica.media_access import media_access
from matricula.urls import urlpatterns as enrollurls
from membership_core.urls import urlpatterns as url_core

urlpatterns = djgentelellaurls + [
    # Con barra final: sin ella Django responde 301 y la sonda del panel lo
    # leeria como no-sano.
    path('health/', health, name='health'),
    path('async_notification/', include('djgentelella.async_notification.urls')),
    path('admin/', admin.site.urls),
    # Certificados y comprobantes de deposito: los decide Django y los sirve
    # nginx con X-Accel-Redirect. ANTES de la ruta generica, que serviria
    # cualquier archivo sin mirar quien pide.
    re_path(r'^media/(?P<path>(?:certificates|bank)/.*)$', media_access,
            name='media_access'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] + url_core + enrollurls
