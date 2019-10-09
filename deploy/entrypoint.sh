#!/bin/bash

chmod +x /MEMBRESIAS/deploy/check_membresias.py
su membresias -c /MEMBRESIAS/deploy/check_membresias.py 

exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/membresias_supervisor.conf
