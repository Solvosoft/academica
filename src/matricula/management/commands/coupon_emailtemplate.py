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
