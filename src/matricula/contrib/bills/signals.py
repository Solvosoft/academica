# -*- coding: UTF-8 -*-
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.dispatch import receiver
from matricula.models import Enroll, Coupon
from .models import Bill
from django.utils.translation import ugettext_lazy as _
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED
from datetime import datetime
from django.utils.encoding import smart_text
from async_notifications.utils import send_email_from_template
from django.views.decorators.csrf import csrf_exempt


@receiver(post_save, sender=Enroll)
def create_bill(sender, **kwargs):
    instance = kwargs['instance']
    if not instance.bill_created and instance.enroll_finished\
            and instance.group.cost > 0:
        instance.bill_created = True

        coupons = Coupon.objects.filter(course=instance.group.course, student=instance.student)
        discount = 0.0
        total = instance.group.cost

        if coupons:
            percentage = sum(coupons.values_list('discount_percentage', flat=True))

            if instance.group.cost > 0:
                discount = instance.group.cost
                total = 0.0

                if percentage == 50:
                    discount = instance.group.cost / 2
                    total = instance.group.cost / 2

        instance.save()

        Bill.objects.create(
            short_description=_("Enroll in %s") % (instance.group),
            description=render_to_string(
                'invoice_enroll.html',
                {
                    'student': instance.student,
                    'enroll': smart_text(instance.group),
                    'discount': discount,
                    'total': total,
                    'date': instance.enroll_date.strftime("%Y-%m-%d %H:%M"),
                    'group': instance.group,
                }
            ),
            amount=total,
            student=instance.student,
            currency=instance.group.currency,
            enrollment=instance
        )

        Coupon.objects.filter(course=instance.group.course, student=instance.student).update(bill=Bill.objects.last(), is_used=True)


@csrf_exempt
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
        except Exception:
            ok = False
            # FIXME do something here
        if ok:
            send_email_from_template(
                'email_invoice_academy', bill.student.user.email, {
                    'bill': bill,
                    'student': bill.student
                },
                enqueued=False,
                user=None)


valid_ipn_received.connect(paypal_bill_paid)
