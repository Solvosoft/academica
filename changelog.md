# Change log file

18/09/2026 — versión 2.0.0

Actualización completa. **Requiere una base de datos nueva**: las migraciones se
regeneraron desde cero.

- Python 3.13, Django 6.0 y djgentelella 0.6.3 (Bootstrap 5, Chart.js 4, DataTables 2).
- `async_notifications` se reemplaza por `djgentelella.async_notification`. Las
  plantillas de correo se crean en la migración de datos, y `load_email_templates`
  las resincroniza.
- Se eliminan django-ckeditor, django-markitup, markdown, djangoajax,
  django-excel/pyexcel, django-simple-math-captcha y otras dependencias sin uso.
  Las exportaciones ahora generan `.xlsx` (openpyxl).
- xhtml2pdf 0.2.20. Los certificados funcionan en la imagen Docker (`rsvg-convert`).
- Catálogos de países y monedas con djgentelella; reemplazan "Monedas de intercambio".
- Celery usa Redis. Docker se separa en roles web/celery/beat con `SERVICE_TYPE`.
- Nuevo `Makefile` (`make help`).
- Instalación: `make up`, o `python manage.py academica_install`.

-------------------

14/11/2021
- Update workload on courses
    `python manage.py load_workload`

05/08/2021
- Update requirements
    `pip install -r requirements.txt`

14/05/2021
- Add template paid_excluded
    `python manage.py add_template_paid_excluded`

12/05/2021
- Update migrations
    `python manage.py migrate`

10/05/2021
 - Update migrations
    `python manage.py update_prod_temp`
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
