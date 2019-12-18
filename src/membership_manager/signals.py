from async_notifications.utils import send_email_from_template
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save,post_delete
from django.dispatch import receiver
from membership_manager.models import Membership, Attention


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

@receiver(pre_save, sender=Attention)
def save_attention(sender, instance, **kwargs):
    if instance.duration == 0 or instance.duration == None:
        start_date = instance.start_date
        end_date = instance.end_date
        diff = start_date - end_date
        total_seconds = abs(diff.total_seconds())
        instance.duration = total_seconds / 3600

@receiver([post_save,post_delete], sender=Attention)
def change_activity_time_elapsed(sender, instance, **kwargs):
    instance.activity.time_elapsed = instance.activity.attentions.aggregate(time_elapsed=Sum("duration"))['time_elapsed']
    instance.activity.save()