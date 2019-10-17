#!/bin/bash

docker run  -p 8025:8025 -p  1025:1025 -d mailhog/mailhog
docker run --name membresias-redis -p 6379:6379 -d redis 
cd src/
celery -A membresias_codigosur worker -l info -B
