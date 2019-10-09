# MEMBRESIAS

Este proyecto ayuda a gestionar membresías de diferentes organizaciones para códigosur


# Installation 
La instalación por defecto se realiza con docker compose

    docker-compose up

# Instalación de desarrollo

Install postgresql 

    sudo apt install postgresql 
    sudo su postgres
    psql 
    \password

Edit this file `/etc/postgresql/9.6/main/pg_hba.conf` changing postgres user from peer to md5
restart the server

    sudo systemctrl postgresql restart 

Install pgadmin III

    sudo apt install pgadmin3

Clone the repository

    git clone git@gitlab.com:solvosoft/membresias.git
    
Install django code 

     virtualenv -p python3 ~/entornos/membresias
     pip install -r requirements.txt
     
 Create the database
 
     python manage.py migrate
     
 Create a superuser 
 
     python manage.py createsuperuser 
 
 Run the development server 
 
     python manage.py runserver
     
# Sending Email on development

    python -m smtpd -c DebuggingServer -n localhost:1025

o también ver https://github.com/mailhog/MailHog
