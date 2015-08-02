# encoding: utf-8

from django.db import models
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class Colon_Exchange(models.Model):
    is_dolar = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Amount"))

@python_2_unicode_compatible
class Bill(models.Model):
    short_description = models.CharField(max_length=300, verbose_name=_("Short description"))
    description = models.TextField(verbose_name=_("Description"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    student = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Student"))
    currency = models.CharField(max_length=3, verbose_name=_("Currency"), default="CRC")
    is_paid = models.BooleanField(default=False)
    paid_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.TextField(max_length=300, null=True, blank=True)
 
    def __str__(self):
        return self.short_description

    class Meta:
        verbose_name = _("Bill")
        verbose_name_plural = _("Bills")

class Sale(models.Model):
    def __init__(self, *args, **kwargs):
        super(Sale, self).__init__(*args, **kwargs)

        # bring in stripe, and get the api key from settings.py
        import stripe
        stripe.api_key = settings.STRIPE_API_KEY
 
        self.stripe = stripe
 
    # store the stripe charge id for this sale
    charge_id = models.CharField(max_length=32)
    bill = models.ForeignKey(Bill)
 
    # you could also store other information about the sale
    # but I'll leave that to you!
 
    def charge(self, price_in_cents, bill, number, exp_month, exp_year, cvc):
        """
        Takes a the price and credit card details: number, exp_month,
        exp_year, cvc.
 
        Returns a tuple: (Boolean, Class) where the boolean is if
        the charge was successful, and the class is response (or error)
        instance.
        """
 
        if self.charge_id:  # don't let this be charged twice!
            return False, Exception(message=_("Already charged."))
 
        try:
            response = self.stripe.Charge.create(
                amount=price_in_cents,
                currency=bill.currency,
                card={
                    "number": number,
                    "exp_month": exp_month,
                    "exp_year": exp_year,
                    "cvc": cvc,
 
                    #### it is recommended to include the address!
                    # "address_line1" : self.address1,
                    # "address_line2" : self.address2,
                    # "daddress_zip" : self.zip_code,
                    # "address_state" : self.state,
                },
                description=bill.description)

            self.charge_id = response.id
            self.bill = bill

        except self.stripe.CardError as ce:
            return False, ce

        return True, response

