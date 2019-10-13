from async_notifications.register import update_template_context
from async_notifications.utils import send_email_from_template
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse

from membership_manager.models import Membership


@receiver(post_save, sender=Membership)
def email(sender, instance, created, **kwargs):
    if created:
        context = [
            ('subject', '¡Te damos la bienvenida Cliente!'),
            ('message', 'Hola cliente!\nNos alegra que decidieras unirte a la familia de Código Sur. Ya puedes '
                        'disfrutar de nuestros servicios.\nSientete libre de contactarnos si nos necesitas o surge '
                        'algún inconveniente.\nTel:8888-888\t\tCorreo:example@mail.com'
                        '\n\nEstamos para servirte.\nCódigo Sur'),
        ]

        code = 'mbs_' + str(instance.id)

        update_template_context(code, 'subscribe_email.html', 'Pago de membresía - Código Sur', context)

        send_email_from_template(code, [instance.contact.email],
                                 context={},
                                 enqueued=False,  # ask about this! Docu says: enqueued if False send the email
                                                  # immediately else enqueued to be sended when send email task run.
                                 user=None,
                                 upfile=None)
    return HttpResponse("Done!")
