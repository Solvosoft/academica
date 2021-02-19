# Pasos para deploy

19/02/2021

### Fixed
    
- Updated permssions to admins academy
    
    `python src/manage.py migrate`

- Translations and grammar

    `python src/manage.py compilemessages`

- Update email context
    `python src/manage.py update_academy_temp`

------------------

26/11/2020

Ejecutar migraciones

    python manage.py migrate

Ejecutar los siguientes comandos para incluir nuevos grupos y notificaciones de correo electrónico

    python manage.py coupon_emailtemplate
    python manage.py permission_groups   
    python manage.py load_email_temp_academy
