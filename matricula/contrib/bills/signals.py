# -*- coding: UTF-8 -*-
from django.db.models.signals import post_save
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.dispatch import receiver
from matricula.models import Enroll
from .models import Bill
from django.utils.translation import ugettext_lazy as _
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED
from datetime import datetime
from django.utils.encoding import smart_text
from django.conf import settings


@receiver(post_save, sender=Enroll)
def create_bill(sender, **kwargs):
    instance = kwargs['instance']
    if not instance.bill_created and instance.enroll_finished\
    and instance.group.cost > 0:
        instance.bill_created = True
        Bill.objects.create(short_description=_("Enroll in %s") % (instance.group),
                            description=render_to_string('invoice.html',
                                    { 'student': instance.student,
                                      'enroll': smart_text(instance.group),
                                      'date': instance.enroll_date.strftime("%Y-%m-%d %H:%M"),
                                      'group': instance.group,
                                    }
                                                        ),
                            amount=instance.group.cost,
                            student=instance.student,
                            currency=instance.group.currency,
                            )
        instance.save()


def paypal_bill_paid(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            bill = Bill.objects.get(pk=ipn_obj.invoice)
            bill.is_paid = True
            bill.paid_date = datetime.now()
            bill.transaction_id = ipn_obj.txn_id
            bill.save()
            ok = True
        except Exception as e:
            ok = False
            # FIXME do something here
        if ok:
            invoice = render_to_string('email_invoice.html', {'bill': bill})
            send_mail(_("Academica Invoice paid"),
                      _("Go to Academica"),
                      settings.DEFAULT_FROM_EMAIL,
                      [bill.student.email],
                      html_message=invoice,
                      fail_silently=False
                      )

valid_ipn_received.connect(paypal_bill_paid)
