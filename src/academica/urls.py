from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from djgentelella.urls import urlpatterns as djgentelellaurls

from academica.health import health
from matricula.urls import urlpatterns as enrollurls
from membership_core.urls import urlpatterns as url_core

urlpatterns = djgentelellaurls + [
    # Con barra final: sin ella Django responde 301 y la sonda del panel lo
    # leeria como no-sano.
    path('health/', health, name='health'),
    path('async_notification/', include('djgentelella.async_notification.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
] + url_core + enrollurls
