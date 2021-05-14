# Change log file

14/05/2021
- Add template paid_excluded
    `python manage.py add_template_paid_excluded`

12/05/2021
- Update migrations
    `python manage.py migrate`

10/05/2021
 - Update migrations
    `python manange update_prod_temp`
    `python manage.py migrate`

19/04/2021

### Template update

 - Update templates
    `python manage.py update_academy_temp`

11/04/2021

### Fixed

- Enable unaccent extension Pg in 
    Run in psql as root:
    `CREATE EXTENSION unaccent;` or 
    
    make the settings.py user as a root user:
    `ALTER ROLE user SUPERUSER;`

12/03/2021

### Fixed 

- Update translations in emails

    `python manage.py compilemessages -l es` 

- Update email templates

    `python manage.py update_academy_temp` 

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
