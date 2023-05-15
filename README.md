# Gestor de cursos

Este proyecto ayuda a gestionar cursos de la Universidad Popular.


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



Clone the repository

    git clone git@gitlab.com:solvosoft/upo.git
    
Install django code 

     virtualenv -p python3 ~/entornos/upo
     pip install -r requirements.txt
     
 Create the database
 
     python manage.py migrate
     python manage.py createcachetable
     
 Create a superuser 
 
     python manage.py createsuperuser 

Compile translations

    python manage.py compilemessages -l es

Update email templates

    python manage.py update_academy_temp

Create permission groups

    python manage.py permission_groups
 
 Run the development server 
 
     python manage.py runserver
     
# Sending Email on development

    python -m smtpd -c DebuggingServer -n localhost:1025

o también ver https://github.com/mailhog/MailHog
 
 

# Create Rabbitmq 

    rabbitmqctl add_user upo upopass
    rabbitmqctl add_vhost upovhost
    rabbitmqctl set_user_tags upo upotag
    rabbitmqctl set_permissions -p upovhost upo ".*" ".*" ".*"