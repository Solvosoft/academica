# -*- coding: UTF-8 -*-

from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import smart_str
from django.conf import settings

from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from matricula.models import Enroll, Coupon, Group, Student
from djgentelella.async_notification.sending import send_email_from_template
from .card_payments import mark_bill_paid
from .models import Bill
from matricula.coupons import apply_coupons


@receiver(post_save, sender=Enroll)
def create_bill(sender, **kwargs):
    instance = kwargs['instance']
    if not instance.bill_created and instance.enroll_finished\
            and instance.group.cost > 0 and not instance.paid_excluded:
        instance.bill_created = True
        instance.save()

        total = instance.group.cost
        bill = Bill.objects.create(
            short_description=_("Enroll in %s") % (instance.group),
            description=render_to_string(
                'invoice_enroll.html',
                {
                    'student': instance.student,
                    'enroll': smart_str(instance.group),
                    'discount': 0,
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
        if Coupon.objects.filter(group=instance.group, student=instance.student).exists():
            apply_coupons(bill)


def paypal_bill_paid(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        bill = Bill.objects.filter(pk=ipn_obj.invoice).first()
        if bill:
            if not bill.is_paid:
                mark_bill_paid(bill, ipn_obj.txn_id)
        else:
            group = Group.objects.filter(pk=ipn_obj.item_name).first()
            student = Student.objects.filter(pk=ipn_obj.item_number).first()
            emails = list(settings.PAYPAL_ERROR_EMAIL_NOFIFY)
            if student:
                emails.append(student.user.email)
            send_email_from_template(
                'invoice_not_found', emails, {
                    'student': student,
                    'domain': settings.MY_PAYPAL_HOST,
                    'transaction_id': ipn_obj.txn_id,
                    'group': group,
                    'amount': ipn_obj.mc_gross,
                    'currency': ipn_obj.mc_currency,
                },
                enqueued=False,
                user=None)

valid_ipn_received.connect(paypal_bill_paid)
