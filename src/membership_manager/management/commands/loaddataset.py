from async_notifications.register import update_template_context
from django.core.management import BaseCommand
from django.utils import timezone
from faker import Faker
from membership_manager.task_utils import *

from membership_core.models import SystemCurrency, Service, RenewalPeriod
from membership_manager.models import Contact, Organization, Membership, MembershipRenew


class Command(BaseCommand):
    help = "Load templates command"
    fake = Faker()
    contacts_num = 10
    memb_num = 2
    fails = 2
    contacts_ids = []
    contact_qset = None
    services_list = [service
                     for service in Service.objects.all()]
    renewal_period_list = [renewal
                     for renewal in RenewalPeriod.objects.all()]
    now = timezone.now()

    def add_organization(self):
        self.contact_qset = Contact.objects.filter(pk__in = self.contacts_ids)
        for contact in self.contact_qset:
            currency = SystemCurrency.objects.get(currency = self.fake.random_element(elements=('CRC','HNL', 'EUR', 'USD', 'ARS')))
            organization = Organization.objects.create(name=f'{self.fake.company()} {self.fake.company_suffix()}',
                                                       initials=self.fake.pystr(min_chars=4, max_chars=4).upper(),
                                                       contact=contact,email=self.fake.email(),cellphone=self.fake.phone_number(),
                                   phone=self.fake.phone_number(), address=self.fake.address(),
                                   country=self.fake.country(),city=self.fake.city(),province=self.fake.city(),
                                   postal_code=self.fake.postalcode(),active=self.fake.boolean(chance_of_getting_true=99),
                                   currency=currency, payment_method=self.fake.random_element(elements=('Cash','Bank transfer', 'Paypal', 'Bitcoins')))

    def create_contacts(self):
        for c in range(self.contacts_num):
            currency = SystemCurrency.objects.get(currency = self.fake.random_element(elements=('CRC','HNL', 'EUR', 'USD', 'ARS')))
            contact = Contact.objects.create(email=self.fake.email(),first_name=self.fake.first_name(),
                                   last_name=self.fake.last_name(), cellphone=self.fake.phone_number(),
                                   phone=self.fake.phone_number(), address=self.fake.address(),
                                   country=self.fake.country(),city=self.fake.city(),province=self.fake.city(),
                                   postal_code=self.fake.postalcode(),active=self.fake.boolean(chance_of_getting_true=99),
                                   currency=currency, payment_method=self.fake.random_element(elements=('Cash','Bank transfer', 'Paypal', 'Bitcoins')))
            self.contacts_ids.append(contact.pk)
        self.add_organization()

    def create_memberships(self):
        for contact in self.contact_qset:
            organizations = contact.organization_set.all()
            for organization in organizations:
                membership = Membership(
                    creation_date= self.now,
                    membership_type=self.fake.random_element(elements=('Personal','Radial', 'Organizacional', 'Global','Honoraria')),
                    contact = contact, organization = organization,name=f'{organization.name} STANDARD',
                    annual_cost=self.fake.pyint(min_value=25, max_value=1000, step=125),
                    currency= organization.currency,description=self.fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
                    renewal_period=self.renewal_period_list[self.fake.pyint(min_value=0, max_value=len(self.renewal_period_list)-1, step=1)],
                    state='active'
                )
                membership.save()
                membership.services.set(self.services_list)

                renew = MembershipRenew.objects.create(
                    creation_date=self.now,
                    membership = membership,
                    start_date=self.now,
                    end_date=self.now+timezone.timedelta(days=7),
                    graceperiod=False,
                    active=True)

    def create_memberships_without_renews(self):
        for contact in self.contact_qset:
            organizations = contact.organization_set.all()
            for organization in organizations:
                membership = Membership(
                    creation_date= self.now,
                    membership_type=self.fake.random_element(elements=('Personal','Radial', 'Organizacional', 'Global','Honoraria')),
                    contact = contact, organization = organization,name=f'{organization.name} STANDARD',
                    annual_cost=self.fake.pyint(min_value=25, max_value=1000, step=125),
                    currency= organization.currency,description=self.fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
                    renewal_period=self.renewal_period_list[self.fake.pyint(min_value=0, max_value=len(self.renewal_period_list)-1, step=1)],
                    state='active'
                )
                membership.save()
                membership.services.set(self.services_list)

    def create_memberships_graceperiod_expired(self):
        for contact in self.contact_qset:
            organizations = contact.organization_set.all()
            for organization in organizations:
                membership = Membership(
                    creation_date= self.now,
                    membership_type=self.fake.random_element(elements=('Personal','Radial', 'Organizacional', 'Global','Honoraria')),
                    contact = contact, organization = organization,name=f'{organization.name} STANDARD',
                    annual_cost=self.fake.pyint(min_value=25, max_value=1000, step=125),
                    currency= organization.currency,description=self.fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
                    renewal_period=self.renewal_period_list[self.fake.pyint(min_value=0, max_value=len(self.renewal_period_list)-1, step=1)],
                    state='graceperiod'
                )
                membership.save()
                membership.services.set(self.services_list)
                MembershipRenew.objects.create(
                    creation_date=self.now - timezone.timedelta(days=30),
                    membership=membership,
                    start_date=self.now - timezone.timedelta(days=30),
                    end_date=self.now - timezone.timedelta(days=15),
                    graceperiod=False,
                    active=True)
                renew = MembershipRenew.objects.create(
                    creation_date=self.now - timezone.timedelta(days=15),
                    membership=membership,
                    start_date=self.now - timezone.timedelta(days=15),
                    end_date=self.now,
                    graceperiod=True,
                    active=True)

    def create_memberships_graceperiod(self):
        for contact in self.contact_qset:
            organizations = contact.organization_set.all()
            for organization in organizations:
                membership = Membership(
                    creation_date= self.now,
                    membership_type=self.fake.random_element(elements=('Personal','Radial', 'Organizacional', 'Global','Honoraria')),
                    contact = contact, organization = organization,name=f'{organization.name} STANDARD',
                    annual_cost=self.fake.pyint(min_value=25, max_value=1000, step=125),
                    currency= organization.currency,description=self.fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
                    renewal_period=self.renewal_period_list[self.fake.pyint(min_value=0, max_value=len(self.renewal_period_list)-1, step=1)],
                    state='graceperiod'
                )
                membership.save()
                membership.services.set(self.services_list)
                MembershipRenew.objects.create(
                    creation_date=self.now - timezone.timedelta(days=30),
                    membership=membership,
                    start_date=self.now - timezone.timedelta(days=30),
                    end_date=self.now,
                    graceperiod=False,
                    active=True)
                renew = MembershipRenew.objects.create(
                    creation_date=self.now,
                    membership=membership,
                    start_date=self.now,
                    end_date=self.now + timezone.timedelta(days=15),
                    graceperiod=True,
                    active=True)

    def create_memberships_inactive(self):
        for contact in self.contact_qset:
            organizations = contact.organization_set.all()
            for organization in organizations:
                membership = Membership.objects.create(
                    creation_date=self.now,
                    membership_type=self.fake.random_element(
                        elements=('Personal', 'Radial', 'Organizacional', 'Global', 'Honoraria')),
                    contact=contact, organization=organization, name=f'{organization.name} STANDARD',
                    annual_cost=self.fake.pyint(min_value=25, max_value=1000, step=125),
                    currency=organization.currency,
                    description=self.fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
                    renewal_period=self.renewal_period_list[self.fake.pyint(min_value=0, max_value=len(self.renewal_period_list)-1, step=1)],
                    state='inactive'
                )
                membership.save()
                membership.services.set(self.services_list)
                MembershipRenew.objects.create(
                    creation_date=self.now - timezone.timedelta(days=30),
                    membership=membership,
                    start_date=self.now - timezone.timedelta(days=30),
                    end_date=self.now,
                    graceperiod=False,
                    active=False)
                renew = MembershipRenew.objects.create(
                    creation_date=self.now,
                    membership=membership,
                    start_date=self.now,
                    end_date=self.now + timezone.timedelta(days=15),
                    graceperiod=True,
                    active=False)

    def call_all_cases(self):
        self.create_memberships()
        self.create_memberships_graceperiod()
        # self.create_memberships_graceperiod_expired()
        # self.create_memberships_without_renews()
        # self.create_memberships_inactive()

    ## ACTIONS MANAGEMENT ##

    def check_with_tasks(self):
        invoice_creation(self.now)
        renew_graceperiod(self.now)
        membership_deactivating(self.now)

    def handle(self, *args, **options):
        self.create_contacts()
        self.call_all_cases()
        # self.check_with_tasks()
