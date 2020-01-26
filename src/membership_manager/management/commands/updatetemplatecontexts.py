from async_notifications.models import TemplateContext
from django.core.management import BaseCommand
from django.db.models import ForeignKey, ManyToOneRel, ManyToManyRel

from membership_manager.models import Membership, Invoice
import json


class Command(BaseCommand):
    help = "Update template context"
    MAX_RECURSION = 2

    def extract_fields(self, model, recursion=0, prefix=''):
        dev_fields = []
        if recursion == self.MAX_RECURSION:
            return []
        for field in model._meta.get_fields():
            if isinstance(field, (ForeignKey, ManyToOneRel)):

                dev_fields += self.extract_fields(field.related_model,
                                    recursion=recursion+1,
                                    prefix=prefix+field.name+".")
            elif isinstance(field, ManyToManyRel):
                pass
            else:
                dev_fields.append((prefix+field.name, field.verbose_name))
        return dev_fields

    def handle(self, *args, **options):
        self.membership_invoice_context('pay_mail')
        self.membership_invoice_context("notification_mail")
        self.membership_context('welcome_mail')
        self.membership_context('expiration_mail')

    def membership_invoice_context(self, code):
        context=TemplateContext.objects.get(code=code)
        context_dic=[
            ('Membresia', self.extract_fields(Membership, prefix='membership.')),
            ('Factura', self.extract_fields(Invoice, prefix='invoice.'))
        ]


        context.context_dic = json.dumps(dict(context_dic))
        context.save()

    def membership_context(self, code):
        context=TemplateContext.objects.get(code=code)
        fields = self.extract_fields(Membership, prefix='membership.')
        context_dic = dict([('Membresía',fields)])
        context.context_dic = json.dumps(context_dic)
        context.save()


