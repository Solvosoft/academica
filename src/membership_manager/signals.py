from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from membership_manager.models import Membership, ActivityReport, Invoice, MembershipRenew
from membership_manager.task_utils import send_welcome_notification
from membership_manager.tasks import task_create_invoice
from allauth.account.signals import user_signed_up
from matricula.models import Student
from django.utils.timezone import now
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse



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


@receiver(user_signed_up)
def user_signed_up_(request, user, **kwargs):
    student = Student(user=user, created_at=now(), confirmed_at=now())
    student.save()
    mail_body = render_to_string("email_welcome.html",
        {
        "url": request.build_absolute_uri(reverse('courses')),
        "user": user,
        })
    send_mail(_('Email confirmation'),
        'Url confirmation %s' % (request.build_absolute_uri(reverse('courses'))),
        settings.DEFAULT_FROM_EMAIL, [user.email],
        html_message=mail_body)
