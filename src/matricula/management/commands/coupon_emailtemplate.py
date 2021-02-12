from django.core.management import BaseCommand
from async_notifications.models import EmailTemplate


class Command(BaseCommand):

    def handle(self, *args, **options):

        file = open('matricula/templates/coupons/coupon_code_notification.html', 'r')

        email_template = EmailTemplate(
            code="coupon_code_notification",
            subject="Cupón de descuento",
            message=file.read()
        )

        email_template.save()
        file.close()

        # Notification email when coupon is updated
        file_update = open('matricula/templates/coupons/coupon_code_notification_update.html', 'r')

        email_template_update = EmailTemplate(
            code="coupon_code_notification_updated",
            subject="Cupón de descuento actualizado",
            message=file_update.read()
        )

        email_template_update.save()
        file_update.close()
