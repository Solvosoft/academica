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
