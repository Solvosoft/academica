from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from membership_manager.models import Membership, ActivityReport, Invoice, MembershipRenew
from membership_manager.task_utils import send_welcome_notification
from membership_manager.tasks import task_create_invoice


@receiver(post_save, sender=Membership)
def welcome_email(sender, instance, created, **kwargs):
    if created and instance.state == "active":
        send_welcome_notification(instance.pk)


# @receiver(post_save, sender=MembershipRenew)
# def rebuild_invoice(sender, instance, created, **kwargs):
#     if instance.active:
#        task_create_invoice(instance.pk)
#    pass
@receiver(post_save, sender=ActivityReport)
def save_attention(sender, instance, **kwargs):

    if kwargs['update_fields'] is not None and 'duration' in kwargs['update_fields']:
        instance.__class__.objects.filter(pk=instance.pk).update(manual_edited=True)

    if not instance.manual_edited or instance.duration == 0:
        instance.manual_edited = False
        total = 0
        for act in instance.attentions.all():
            d = act.end_date - act.start_date
            total += d.days*24 + d.seconds / 60 / 60
        instance.duration = total
        instance.__class__.objects.filter(pk=instance.pk).update(duration=int(total))


@receiver([pre_delete], sender=Invoice)
def remove_invoice_pdf(sender, instance, using,**kwargs):
    if instance.pdf_invoice:
        instance.pdf_invoice.delete(False)
