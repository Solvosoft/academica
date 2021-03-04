#!/bin/bash

docker run -d --rm --name upo-mail -p 8025:8025 -p  1025:1025 -d mailhog/mailhog
docker run -d --rm --name upo-rabbitmq -p 5672:5672 -d rabbitmq:3

echo "Esperando el inicio de rabbitmq ..." && sleep 20
cd src/
celery -A upo worker -l info -B --scheduler django_celery_beat.schedulers:DatabaseScheduler

docker rm -f upo-mail
docker rm -f upo-rabbitmq
