from async_notifications.register import update_template_context


def load_email_temp_academica():
    update_template_context(
        'new_user_created_academy', 'Correo de bienvenida',
        [('user'), ('student'), ('url')],
        'email_confirmation.html', as_template=True)

    update_template_context(
        'email_welcome_academy', 'Correo de confirmación',
        [('url'), ('student')], 'email_welcome.html', as_template=True)

    update_template_context(
        'email_open_group', 'Correo de apertura de grupo',
        [('group'), ('url')], 'email_open_group.html', as_template=True)

    update_template_context(
        'email_preenroll_success', 'Correo de pre-inscripción exitosa',
        [('group'), ('url')], 'email_preenroll_success.html', as_template=True)
    
    update_template_context(
        'email_enroll_success', 'Correo de inscripción exitosa',
        [('group'), ('url')], 'email_enroll_success.html', as_template=True)

    update_template_context(
        'email_close_group', 'Correo de cierre de grupo',
        [('group'), ('url')], 'email_close_group.html', as_template=True)

    update_template_context(
        'email_recovery_academy', 'Correo de recuperación de contraseña',
        [('user'), ('student'), ('url')], 'email_recovery.html',
        as_template=True)

    update_template_context(
        'email_invoice_academy', 'Correo de confirmación de pago',
        [('bill'), ('student'), ('bill_description_safe')],
        'email_invoice.html', as_template=True)

    update_template_context(
        'set_email_first_academy', 'Correo de configuración de contraseña',
        [('url'), ('student')], 'set_email_first.html',
        as_template=True)

    update_template_context(
        'new_user_created_membership', 'Nueva usuaria creada en la plataforma',
        [('user'), ('domain')], 'gentelella/registration/new_user.html',
        as_template=True)
    
    update_template_context(
        'new_professor_created_academy', 'Correo de bienvenida',
        [('user'), ('professor'), ('url')],
        'welcome_professor.html', as_template=True)

    update_template_context(
        'reset_password_academy', 'Correo de configuración de contraseña',
        [('domain'), ('user')], 'set_password_academy.html',
        as_template=True)
