#!/bin/bash

docker run -d --rm --name membresias-mail -p 8025:8025 -p  1025:1025 -d mailhog/mailhog
docker run -d --rm --name membresias-redis -p 6379:6379 -d redis 
cd src/
celery -A membresias_codigosur worker -l info -B

docker rm -f membresias-mail
docker rm -f membresias-redis
