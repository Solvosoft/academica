#!/bin/bash
# Instala o actualiza Académica. Lo lanzan el `bootstrap.job` (sin argumentos)
# y el `lifecycle.upgrade` (--upgrade) del AppPack de la plataforma, NUNCA el
# arranque de un servicio: con réplicas, `academica_install` en cada arranque
# serían migraciones en paralelo sobre la misma base.
#
#   /run/install.sh             instalación nueva
#   /run/install.sh --upgrade   después de cambiar la imagen
#
# El job corre como root (hereda el entorno del servicio web, no su usuario);
# todo lo de Django va como `academica`, igual que en el entrypoint.
set -euo pipefail

MODE="install"
[[ "${1:-}" == "--upgrade" ]] && MODE="upgrade"

cd /app/src
as_app() { runuser -p -u academica -- "$@"; }

echo "install.sh: modo $MODE"

# El media es un bind del host compartido por el web y el worker (los
# certificados los genera el worker). Si el directorio lo creó el daemon, es de
# root y ni la instalación ni la app podrían escribir en él.
mkdir -p "${MEDIA_ROOT:-/app/media/}"
chown academica:academica "${MEDIA_ROOT:-/app/media/}"

# Migraciones, tabla de caché, grupos de permisos y plantillas de correo.
# Idempotente: es lo mismo que corre `make install` en local.
as_app python manage.py academica_install

if [[ "$MODE" == "upgrade" ]]; then
  echo "install.sh: upgrade terminado"
  exit 0
fi

# El administrador inicial sale del ledger del panel (DJANGO_SUPERUSER_*). Se
# crea SOLO si no existe ningún superusuario: volver a correr la instalación no
# pisa una contraseña que la persona ya cambió.
if [[ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]]; then
  as_app python manage.py shell -c '
import os
from django.contrib.auth import get_user_model

User = get_user_model()
if User.objects.filter(is_superuser=True).exists():
    print("install.sh: ya hay un superusuario, no se toca")
else:
    User.objects.create_superuser(
        os.environ["DJANGO_SUPERUSER_USERNAME"],
        os.environ.get("DJANGO_SUPERUSER_EMAIL", ""),
        os.environ["DJANGO_SUPERUSER_PASSWORD"],
    )
    print("install.sh: superusuario %s creado" % os.environ["DJANGO_SUPERUSER_USERNAME"])
'
else
  echo "install.sh: sin DJANGO_SUPERUSER_PASSWORD, no se crea administrador"
fi

echo "install.sh: install terminado"
