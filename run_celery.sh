#!/bin/bash

docker run --name membresias-redis -p 6379:6379 -d redis 
cd src/
celery -A membresias_codigosur worker -l info -B
