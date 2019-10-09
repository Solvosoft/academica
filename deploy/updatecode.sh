#!/bin/bash

rsync -apu --stats --exclude /MEMBRESIAS/src/membresias_codigosur/settings.py  /opt/membresias/src /MEMBRESIAS/src
python src/manage.py collectstatic --no-input
python src/manage.py migrate --no-input
