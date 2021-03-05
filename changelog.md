# Change log file

05/03/2021
### Fixed 

- Update email templates

    `python manage.py update_academy_temp` 

- Translations and grammar

    `python manage.py compilemessages -l es` 

-------------------

02/03/2021

### Fixed
    
- Remove tables related with membership_manager and fix grammar error in legacy MenuItem model.
    
    `python manage.py migrate`

- Translations and grammar

    `python manage.py compilemessages -l es` 

- Update email templates

    `python manage.py update_academy_temp`

- Update permission groups

    `python manage.py permission_groups`

------------------

19/02/2021

### Fixed
    
- Updated permssions to admins academy
    
    `python manage.py migrate`

- Translations and grammar

    `python manage.py compilemessages -l es` 

- Update email context
    `python manage.py update_academy_temp`

------------------

26/11/2020

Ejecutar migraciones

    python manage.py migrate

Ejecutar los siguientes comandos para incluir nuevos grupos y notificaciones de correo electrónico

    python manage.py coupon_emailtemplate
    python manage.py permission_groups   
    python manage.py load_email_temp_academy
