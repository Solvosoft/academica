from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from django.db.models.signals import post_save
from django.dispatch import receiver

from membership_manager.models import Membership


@receiver(post_save, sender=Membership)
def welcome_email(sender, instance, created, **kwargs):
    if created:
        context = [
            ('membership', instance),
        ]

        send_email_from_template('welcome_mail', [instance.contact.email],
                                 context={},
                                 enqueued=False,  # ask about this! Docu says: enqueued if False send the email
                                                  # immediately else enqueued to be sended when send email task run.
                                 user=None,
                                 upfile=None)
