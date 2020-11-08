from django.core.management import BaseCommand

from membership_telbot_manager.models import TelegramNotificationTemplate


class Command(BaseCommand):



    def handle(self, *args, **options):

        file_list = ["expiration_message", "help_dialog", "invoices", "memberships", "notification_message"]
        names_templates = {
            'expiration_message': "Mensaje de expiración",
            'help_dialog': 'Diálogo de ayuda',
            'invoices': 'Facturas',
            'memberships': 'Membresías',
            'notification_message': 'Mensaje de notificación'
        }


        for name in file_list:
            file = open('membership_telbot_manager/templates/'+name+'.txt', 'r')
            template = TelegramNotificationTemplate(
                name=names_templates[name],
                description=file.read()
            )
            template.save()
            file.close()
