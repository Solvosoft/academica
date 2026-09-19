"""
Sonda de salud para la plataforma de despliegue.

`/health/` responde 200 solo si la base y el broker de Celery contestan; 503 si
falla cualquiera. La usan el healthcheck del panel (health.http.path del
AppPack) y el rollout del autodeploy, que pausa si un tenant no queda sano.

No requiere sesión: la consulta un proceso, no una persona. Y no devuelve el
detalle del error, solo qué pieza falló.
"""
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from kombu import Connection


def _database_ok():
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception:
        return False


def _broker_ok():
    # Por kombu y no con un cliente de Redis: el broker de la plataforma es
    # RabbitMQ (amqp://), y localmente Redis. kombu habla los dos.
    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        return True
    try:
        with Connection(settings.CELERY_BROKER_URL, connect_timeout=3) as conn:
            conn.ensure_connection(max_retries=1)
        return True
    except Exception:
        return False


def health(request):
    checks = {"database": _database_ok(), "broker": _broker_ok()}
    status = 200 if all(checks.values()) else 503
    return JsonResponse({key: "ok" if ok else "error" for key, ok in checks.items()},
                        status=status)
