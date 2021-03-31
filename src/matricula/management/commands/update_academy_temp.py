from django.core.management import BaseCommand
from matricula.utils import load_email_temp_academica
from async_notifications.models import TemplateContext, EmailTemplate

from django.conf import settings


class Command(BaseCommand):
    help = "Update email templates in académica"

    def handle(self, *args, **options):
        templates = [
            'new_user_created_academy',
            'email_welcome_academy',
            'email_open_group',
            'email_preenroll_success',
            'email_enroll_success',
            'email_close_group',
            'email_recovery_academy',
            'email_invoice_academy',
            'set_email_first_academy',
            'new_user_created_membership',
            'new_professor_created_academy',
            'reset_password_academy',
            'email_enroll_rejected',
            'invoice_not_found',
            'preenroll_success',
        ]
        TemplateContext.objects.filter(code__in=templates).delete()
        EmailTemplate.objects.filter(code__in=templates).delete()
        load_email_temp_academica()

        file = open(settings.BASE_NOCODE_DIR / 'src/matricula/templates/coupons/coupon_code_notification.html', 'r')

        email_template = EmailTemplate.objects.get(code="coupon_code_notification")
        email_template.message = file.read()
        email_template.subject = "¡Felicidades! Has recibido un cupón de descuento para tu curso - UPO"
        email_template.save()
        file.close()

        # Notification email when coupon is updated
        file_update = open(settings.BASE_NOCODE_DIR / 'src/matricula/templates/coupons/coupon_code_notification_update.html', 'r')

        email_template_update = EmailTemplate.objects.filter(code="coupon_code_notification_updated")
        template = email_template_update.first()
        if template:
            template.message = file_update.read()
            template.subject = "¡Felicidades de nuevo! Tu cupón de descuento ha sido actualizado - UPO"
            template.save()
        else:
            email_template_update = EmailTemplate(
                code="coupon_code_notification_updated",
                subject="¡Felicidades de nuevo! Tu cupón de descuento ha sido actualizado - UPO",
                message=file_update.read()
            )
            email_template_update.save()
        file_update.close()

