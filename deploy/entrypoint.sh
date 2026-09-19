#!/bin/bash
#
# Punto de entrada de la imagen. SERVICE_TYPE elige el rol del contenedor:
#   web    -> gunicorn + nginx (supervisor)
#   celery -> worker de celery
#   beat   -> planificador de celery (django_celery_beat)
#   all    -> web + worker + beat en un solo contenedor
#   dev    -> runserver en :8000 + worker con beat embebido
set -e

cd /app/src
mkdir -p /run/logs/ "${MEDIA_ROOT:-/app/media/}"
chown -R academica:academica /run/logs/ "${MEDIA_ROOT:-/app/media/}"

# Con argumentos, se ejecutan tal cual y no se arranca ningun rol. El motor de
# AppPacks lanza el bootstrap.job y el lifecycle.upgrade asi (el comando va como
# Args del contenedor) y el job hereda SERVICE_TYPE=web del servicio: sin esto
# levantaria nginx+gunicorn en vez de /run/install.sh y no terminaria nunca
# (medido con payments, 2026-09-18).
if [ "$#" -gt 0 ]; then
  exec "$@"
fi

# Migraciones, tabla de caché, grupos y plantillas de correo (idempotente).
# Con varias réplicas conviene correrlo una sola vez: ACADEMICA_BOOT_INSTALL=false
# en los demás contenedores. El AppPack lo apaga en TODOS y deja la instalacion
# a /run/install.sh, que corre una vez y con compuerta.
if [ "${ACADEMICA_BOOT_INSTALL:-true}" = "true" ]; then
  runuser -p -u academica -- python manage.py academica_install
fi

case "${SERVICE_TYPE:-web}" in
  web)
    python /app/nginx_personalize.py
    exec supervisord -n -c /etc/supervisor/supervisord.conf
    ;;
  celery)
    exec runuser -p -u academica -- celery -A academica worker -l info -c "${CELERY_CONCURRENCY:-2}"
    ;;
  beat)
    exec runuser -p -u academica -- celery -A academica beat -l info \
      --scheduler django_celery_beat.schedulers:DatabaseScheduler --pidfile=/tmp/celerybeat.pid
    ;;
  all)
    python /app/nginx_personalize.py
    sed -i 's/autostart=false/autostart=true/' /etc/supervisor/conf.d/academica.conf
    exec supervisord -n -c /etc/supervisor/supervisord.conf
    ;;
  dev)
    runuser -p -u academica -- celery -A academica worker -l info -B \
      --scheduler django_celery_beat.schedulers:DatabaseScheduler &
    exec runuser -p -u academica -- python manage.py runserver 0.0.0.0:8000
    ;;
  *)
    echo "ERROR: SERVICE_TYPE debe ser web, celery, beat, all o dev"
    exit 1
    ;;
esac
