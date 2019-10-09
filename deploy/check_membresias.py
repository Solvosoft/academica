#!/usr/local/bin/python

import random
import string
import os
import re
import time
from distutils.dir_util import copy_tree
RUNPATH="/MEMBRESIAS"
RUNSRC='/MEMBRESIAS/src'


def randomString(stringLength=40):
    """Generate a random string of fixed length """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))

def debug_false(dev):
    dev = dev.replace("DEBUG = True", "DEBUG = False")
    return dev

def create_new_key(dev):
    conf = r"SECRET_KEY = '.*'"
    dev = re.sub(conf, "SECRET_KEY = '"+randomString()+"'", dev)
    return dev

def change_db_props(dev):
    usesqlite=os.getenv('USE_SQLITE', 'true').lower() == "true"
    if usesqlite:
       dbtext =  """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
"""
       ini = dev.find("# databaseconf")
       fin = dev.find("# enddatabaseconf")
       dev = dev[:ini]+dbtext+dev[fin+len("# enddatabaseconf"):]
    return dev
           
def check_settings_params(path):
    with open(path, 'r') as arch:
        dev = arch.read()
    dev = create_new_key(dev);
    dev = debug_false(dev)
    dev = change_db_props(dev);
    dev = add_memcached(dev);
    with open(path, 'w') as arch:
        arch.write(dev)

def add_memcached(dev):
    extras = ""
    if os.getenv('USE_MEMCACHED', 'true').lower() == 'true':
        extras = """

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': os.getenv('MEMCACHED_HOST', 'memcached:11211'),
    }
}

    """
    return dev + extras

def wait_for_db():
    import psycopg2
    usesqlite=os.getenv('USE_SQLITE', 'true') == "true"
    waitfordb = os.getenv('WAIT_DB', 'true').lower() == 'true'
    if waitfordb and not usesqlite:
        not_ok=True
        while not_ok :
            try:
                db = psycopg2.connect(
                            host=os.getenv('DB_HOST', 'localhost'), 
                            port=os.getenv('DB_PORT', '5432'), 
                            dbname=os.getenv('DB_NAME', 'registro-db'),
                            user=os.getenv('DB_USER', 'registro-user'), 
                            password=os.getenv('DB_PASSWORD', 'registro12345')
                    )

                not_ok=False
            except Exception as e:
                print(e)
            if not_ok:
                print("Waiting for database 5 seconds")
                time.sleep(5)                

if not os.path.exists(RUNSRC):
#if not os.listdir() :
    copy_tree("/opt/membresias/src", RUNSRC)
    os.chdir(RUNPATH)
    check_settings_params(RUNSRC+"/membresias_codigosur/settings.py")
    wait_for_db()
    os.system("python src/manage.py collectstatic")
    os.system("python src/manage.py migrate")
