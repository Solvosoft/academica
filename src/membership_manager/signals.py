from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from django.core.signals import request_finished
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from membership_manager.models import Membership, MembershipRenew


@receiver(post_save, sender=Membership)
def welcome_email(sender, instance, created, **kwargs):
    if created:
        email = ''
        if instance.contact:
            email = instance.contact.email
        else:
            email = instance.organization.contact.email
        send_email_from_template('welcome_mail', [email],
                                 context={
                                     'membership': instance

                                 },
                                 enqueued=False,  # ask about this! Docu says: enqueued if False send the email
                                                  # immediately else enqueued to be sended when send email task run.
                                 user=None,
                                 upfile=None)

