# Pasos para deploy

Ejecutar migraciones

    python manage.py migrate

Ejecutar los siguientes comandos para incluir nuevos grupos y notificaciones de correo electrónico

    python manage.py coupon_emailtemplate
    python manage.py permission_groups   
    python manage.py load_email_temp_academy
