# Gestor de membresías de Código Sur

Este proyecto crea un sistema para la gestión de las membresías existentes en Código Sur, está hecho en 
Django 2.2.

# Instalación 

Los pasos son comunes a cualquier intalación de Django.

    virtualenv -p python3.6 ~/entornos/membresias
    source ~/entornos/membresias/bin/activate
    git clone git@gitlab.codigosur.com:luisza/membership_management.git
    cd membership_management
    pip install -r requirements.txt
    
Luego hacemos las migraciones 

    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver 

Esto activa el entorno de desarrollo.
