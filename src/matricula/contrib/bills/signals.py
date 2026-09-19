# -*- coding: UTF-8 -*-
from datetime import datetime

from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import smart_str
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import mark_safe
from django.conf import settings

from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from matricula.models import Enroll, Coupon, Group, Student
from djgentelella.async_notification.sending import send_email_from_template
from .models import Bill


@receiver(post_save, sender=Enroll)
def create_bill(sender, **kwargs):
    instance = kwargs['instance']
    if not instance.bill_created and instance.enroll_finished\
            and instance.group.cost > 0 and not instance.paid_excluded:
        instance.bill_created = True
        instance.save()

        coupons = Coupon.objects.filter(group=instance.group, student=instance.student, is_used=False)
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

        Bill.objects.create(
            short_description=_("Enroll in %s") % (instance.group),
            description=render_to_string(
                'invoice_enroll.html',
                {
                    'student': instance.student,
                    'enroll': smart_str(instance.group),
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

        if coupons:

            coupons.update(bill=Bill.objects.last(), is_used=True)


@csrf_exempt
def paypal_bill_paid(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        bill = Bill.objects.filter(pk=ipn_obj.invoice).first()
        if bill:
            bill.is_paid = True
            bill.paid_date = datetime.now()
            bill.transaction_id = ipn_obj.txn_id
            bill.save()
            send_email_from_template(
                'email_invoice_academy', bill.student.user.email, {
                    'bill': bill,
                    'domain': settings.MY_PAYPAL_HOST,
                    'bill_description_safe': mark_safe(bill.description),
                    'student': bill.student,
                },
                enqueued=False,
                user=None)
        else:
            group = Group.objects.filter(pk=ipn_obj.item_name).first()
            student = Student.objects.filter(pk=ipn_obj.item_number).first()
            transaction_id = ipn_obj.txn_id
            amount = ipn_obj.mc_gross
            currency = ipn_obj.mc_currency
            emails = list(settings.PAYPAL_ERROR_EMAIL_NOFIFY)
            emails.append(bill.student.user.email)
            send_email_from_template(
                'invoice_not_found', emails, {
                    'student': student,
                    'domain': settings.MY_PAYPAL_HOST,
                    'transaction_id': transaction_id,
                    'group': group,
                    'amount': amount,
                    'currency': currency,
                },
                enqueued=False,
                user=None)

valid_ipn_received.connect(paypal_bill_paid)
