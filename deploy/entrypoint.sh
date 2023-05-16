#!/bin/bash

cd /app/src

mkdir -p /run/logs/
chown -R academica:academica /app
runuser -p  -c "python manage.py migrate" academica
runuser -p  -c "python manage.py createcachetable" academica


if [ -z "$DEVELOPMENT" ]; then
  python /app/nginx_personalize.py
  supervisord -n
else
  runuser -p -c "celery -A academica worker  -l info -B" organilab &
  runuser -p -c "python manage.py runserver 0.0.0.0:8000" organilab
fi

