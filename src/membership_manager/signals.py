from async_notifications.utils import send_email_from_template
from django.db.models.signals import post_save
from django.dispatch import receiver
from membership_manager.models import Membership


@receiver(post_save, sender=Membership)
def welcome_email(sender, instance, created, **kwargs):
    if created:
        if instance.contact:
            email = instance.contact.email
        else:
            email = instance.organization.contact.email
        send_email_from_template('welcome_mail', [email],
                                 context={
                                     'membership': instance
                                 },
                                 enqueued=False,
                                 user=None,
                                 upfile=None)

