#!/bin/bash

docker run -d --rm --name membresias-mail -p 8025:8025 -p  1025:1025 -d mailhog/mailhog
docker run -d --rm --name membresias-rabbitmq -p 5672:5672 -d rabbitmq:3

echo "Esperando el inicio de rabbitmq ..." && sleep 20
cd src/
celery -A membresias_codigosur worker -l info -B

docker rm -f membresias-mail
docker rm -f membresias-rabbitmq
