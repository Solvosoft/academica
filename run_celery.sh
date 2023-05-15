#!/bin/bash

docker run -d --rm --name academica-mail -p 8025:8025 -p  1025:1025 -d mailhog/mailhog
docker run -d --rm --name academica-rabbitmq -p 5672:5672 -d rabbitmq:3

echo "Esperando el inicio de rabbitmq ..." && sleep 20
cd src/
celery -A academica worker -l info -B --scheduler django_celery_beat.schedulers:DatabaseScheduler

docker rm -f academica-mail
docker rm -f academica-rabbitmq
