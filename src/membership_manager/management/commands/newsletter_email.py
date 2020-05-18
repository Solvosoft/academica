from django.core.management import BaseCommand

from async_notifications.newsletter_utils import get_connections_config, get_from_email
from django.core import mail

class Command(BaseCommand):
    help = "Load templates command"

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='+', type=str)

    def handle(self, *args, **options):
        messages = []
        print(repr(get_connections_config()))
        with mail.get_connection(**get_connections_config()) as connection:
            message = mail.EmailMessage('test email server',
                            "This is a email test from newsletter functionality",
                                        get_from_email(),
                                        options['email'],
                                        connection=connection
                                        )
            message.content_subtype = "html"
            messages.append(message)
            print("Sent ", connection.send_messages(messages))