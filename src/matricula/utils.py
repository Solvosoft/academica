from async_notifications.register import update_template_context


def load_email_temp_academica():
    update_template_context(
        'new_user_created_academy', 'Sólo un paso más para registrarte - UPo.',
        [('user'), ('student'), ('url'), ('domain')],
        'email_confirmation.html', as_template=True)

    update_template_context(
        'email_welcome_academy', 'Correo de confirmación',
        [('url'), ('student'), ('domain')], 'email_welcome.html', as_template=True)

    update_template_context(
        'email_open_group', 'Correo de apertura de grupo',
        [('group'), ('url'), ('domain')], 'email_open_group.html', as_template=True)

    update_template_context(
        'email_preenroll_success', 'Tu PRE-INSCRIPCIÓN ha sido aceptada - UPo',
        [('group'), ('url'), ('domain')], 'email_preenroll_success.html', as_template=True)

    update_template_context(
        'email_enroll_success', 'Tu MATRÍCULA en el curso ha sido aceptada - UPo',
        [('group'), ('url'), ("domain"), ('hours_to_pay')], 'email_enroll_success.html', as_template=True)

    update_template_context(
        'email_close_group', 'Correo de cierre de grupo',
        [('group'), ('url'), ("domain")], 'email_close_group.html', as_template=True)

    update_template_context(
        'email_recovery_academy', 'Correo de recuperación de contraseña',
        [('user'), ('student'), ('url'), ("domain")], 'email_recovery.html',
        as_template=True)

    update_template_context(
        'email_invoice_academy', 'Correo de confirmación de pago',
        [('bill'), ('student'), ('bill_description_safe'), ("domain")],
        'email_invoice.html', as_template=True)

    update_template_context(
        'set_email_first_academy', 'Sólo un paso más para registrarte - UPo.',
        [('url'), ('student'), ("domain")], 'set_email_first.html',
        as_template=True)

    update_template_context(
        'new_user_created_membership', 'Nuevo usuarie registrade en la plataforma',
        [('user'), ('domain')], 'gentelella/registration/new_user.html',
        as_template=True)

    update_template_context(
        'new_professor_created_academy', 'Correo de bienvenida',
        [('user'), ('professor'), ('url'), ("domain")],
        'welcome_professor.html', as_template=True)

    update_template_context(
        'reset_password_academy', 'Correo de configuración de contraseña',
        [('domain'), ('user'), "domain"], 'set_password_academy.html',
        as_template=True)

    update_template_context(
        'email_enroll_rejected', 'Lo sentimos, Tu MATRÍCULA en el curso NO ha sido aceptada - UPo',
        [('group'), ('url'), ("domain")], 'email_enroll_rejected.html', as_template=True)

    update_template_context("coupon_code_notification",
                            "¡Felicidades! Has recibido un cupón de descuento para tu curso - UPO",
                            [('coupon'), ("domain")], 'coupons/coupon_code_notification.html',
                            as_template=True)

    update_template_context("coupon_code_notification_updated",
                            "¡Felicidades de nuevo! Tu cupón de descuento ha sido actualizado - UPO",
                            [('coupon'), ("domain")], 'coupons/coupon_code_notification_update.html',
                            as_template=True)
    update_template_context(
        'email_enroll_removed', 'Lo sentimos, Tu MATRÍCULA ha sido eliminada por no realizarse el pago',
        [('group'), ("domain"), ("hours_to_pay")], 'email_enroll_removed.html', as_template=True)

    update_template_context(
        'invoice_not_found', 'Correo de notificación de error en pago paypal',
        [('student'), ('domain'), ('transaction_id'), ("group"), ('amount'), ('currency')],
        'email_invoice_error.html', as_template=True)

    update_template_context(
        'preenroll_success', 'Tu pre-inscripción en el curso ha sido aceptada - UPo',
        [('group'), ('url'), ("domain")], 'preenroll_success.html', as_template=True)


MONTHS = {1: 'Enero',
          2: 'Febrero',
          3: 'Marzo',
          4: 'Abril',
          5: 'Mayo',
          6: 'Junio',
          7: 'Julio',
          8: 'Agosto',
          9: 'Septiembre',
          10: 'Octubre',
          11: 'Noviembre',
          12: 'Diciembre',
          }


def get_label_months(month):
    if not isinstance(month, int):
        month = int(month)
    return MONTHS[month]
