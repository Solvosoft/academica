import json

from django.template.loader import get_template

from djgentelella.async_notification.registry import register_context

# Variables de contexto que no son modelos y que se envían en todos los correos.
BASE_VARIABLES = {
    'url': 'Enlace de la acción principal del correo',
    'domain': 'Dominio del sitio (esquema + host)',
}
GROUP = {'group': 'matricula.Group'}
STUDENT = {'student': 'matricula.Student'}
USER = {'user': 'auth.User'}

# (código, asunto, plantilla, modelos, variables adicionales)
EMAIL_TEMPLATES = [
    ('new_user_created_academy', 'Sólo un paso más para registrarte - Academica.',
     'email_confirmation.html', {**USER, **STUDENT}, {}),
    ('email_welcome_academy', 'Correo de confirmación',
     'email_welcome.html', STUDENT, {}),
    ('email_open_group', 'Correo de apertura de grupo',
     'email_open_group.html', GROUP, {}),
    ('email_preenroll_success', 'Tu PRE-INSCRIPCIÓN ha sido aceptada',
     'email_preenroll_success.html', GROUP, {}),
    ('email_enroll_success', 'Tu MATRÍCULA en el curso ha sido aceptada',
     'email_enroll_success.html', GROUP,
     {'hours_to_pay': 'Horas disponibles para realizar el pago'}),
    ('email_close_group', 'Correo de cierre de grupo',
     'email_close_group.html', GROUP, {}),
    ('email_recovery_academy', 'Correo de recuperación de contraseña',
     'email_recovery.html', {**USER, **STUDENT}, {}),
    ('email_invoice_academy', 'Correo de confirmación de pago',
     'email_invoice.html', {'bill': 'bills.Bill', **STUDENT},
     {'bill_description_safe': 'Descripción de la factura (HTML)'}),
    ('set_email_first_academy', 'Sólo un paso más para registrarte.',
     'set_email_first.html', STUDENT, {}),
    ('new_user_created_membership', 'Nuevo usuarie registrade en la plataforma',
     'gentelella/registration/new_user.html', USER, {}),
    ('new_professor_created_academy', 'Correo de bienvenida',
     'welcome_professor.html', {**USER, 'professor': 'matricula.Professor'}, {}),
    ('email_enroll_rejected', 'Lo sentimos, Tu MATRÍCULA en el curso NO ha sido aceptada',
     'email_enroll_rejected.html', GROUP, {}),
    ('coupon_code_notification',
     '¡Felicidades! Has recibido un cupón de descuento para tu curso',
     'coupons/coupon_code_notification.html', {'coupon': 'matricula.Coupon'}, {}),
    ('coupon_code_notification_updated',
     '¡Felicidades de nuevo! Tu cupón de descuento ha sido actualizado',
     'coupons/coupon_code_notification_update.html', {'coupon': 'matricula.Coupon'}, {}),
    ('email_enroll_removed',
     'Lo sentimos, Tu MATRÍCULA ha sido eliminada por no realizarse el pago',
     'email_enroll_removed.html', GROUP,
     {'hours_to_pay': 'Horas disponibles para realizar el pago'}),
    ('invoice_not_found', 'Correo de notificación de error en pago paypal',
     'email_invoice_error.html', {**STUDENT, **GROUP},
     {'transaction_id': 'Identificador de la transacción',
      'amount': 'Monto pagado', 'currency': 'Moneda del pago'}),
    ('enroll_paid_excluded', 'Correo de beca completa asignada',
     'enroll_paid_excluded.html', {**USER, **GROUP}, {}),
]


def register_email_contexts():
    """Registra en djgentelella las variables disponibles de cada plantilla."""
    for code, subject, _template, models, extra_variables in EMAIL_TEMPLATES:
        register_context(code, subject, models=models,
                         extra_variables={**BASE_VARIABLES, **extra_variables})


def load_email_templates(email_template_model=None, overwrite=False):
    """
    Crea las plantillas de correo (``EmailTemplate``) a partir de los .html.

    Es idempotente: solo crea las que faltan, salvo que ``overwrite`` sea
    True. Se usa desde la migración de datos y desde el comando
    ``load_email_templates`` (en la migración se le pasa el modelo histórico).
    """
    if email_template_model is None:
        from djgentelella.async_notification.models import EmailTemplate
        email_template_model = EmailTemplate
    created = []
    for code, subject, template_name, _models, _extra in EMAIL_TEMPLATES:
        message = get_template(template_name).template.source
        exists = email_template_model.objects.filter(code=code).exists()
        if exists and not overwrite:
            continue
        email_template_model.objects.update_or_create(
            code=code, defaults={'subject': subject, 'message': message})
        created.append(code)
    return created


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


def organization_names(raw):
    """
    Nombres de organización de un estudiante.

    El campo se guarda como JSON de tagify (``[{"value": "UCR"}, ...]``), pero
    hay registros con texto plano; ambos casos devuelven una lista de nombres.
    """
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return [raw]
    if isinstance(data, dict):
        data = [data]
    if isinstance(data, list):
        return [str(item['value']) if isinstance(item, dict) and 'value' in item else str(item)
                for item in data]
    return [raw]


def count_students_by_organization(students):
    """
    Cantidad de estudiantes por organización, comparando el nombre exacto sin
    distinguir mayúsculas ("org" y "Org" son la misma; "otraorg" no cuenta como
    "org"). Devuelve {nombre en formato título: cantidad} ordenado por nombre.
    """
    counts = {}
    for organization in students.values_list('organization', flat=True):
        for name in {name.strip().lower() for name in organization_names(organization) if name.strip()}:
            counts[name] = counts.get(name, 0) + 1
    return {name.title(): counts[name] for name in sorted(counts)}
