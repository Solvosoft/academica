from membership_core.models import SystemCurrency
from membership_manager.models import Organization, Contact
from membership_manager.tests.utils import create_contacts

from faker import Faker
from random import randint
fake = Faker()

def create_memberships():
    create_contacts(2)
    contact = None
    currencies_list = list(SystemCurrency.objects.all())
    currency = currencies_list[randint(0, len(currencies_list) - 1)]
    contacts_list = list(Contact.objects.all())
    organization = Organization(name=f'{fake.company()} {fake.company_suffix()}',
                            initials=fake.pystr(min_chars=4, max_chars=4).upper(),
                            contact=contact, email="orga@sincontacto.com"
                            , cellphone=fake.phone_number(),
                            phone=fake.phone_number(), address=fake.address(),
                            country=fake.country(), city=fake.city()
                            , province=fake.city(),
                            postal_code=fake.postalcode()
                            , active=True,
                            currency=currency, payment_method=fake.random_element
    (elements=('Cash', 'Bank transfer', 'Paypal', 'Bitcoins')))

    organization.save()
    contact=contacts_list[0]
    organization2 = Organization(name=f'{fake.company()} {fake.company_suffix()}',
                            initials=fake.pystr(min_chars=4, max_chars=4).upper(),
                            contact=contact, email="orga@concontacto.com"
                            , cellphone=fake.phone_number(),
                            phone=fake.phone_number(), address=fake.address(),
                            country=fake.country(), city=fake.city()
                            , province=fake.city(),
                            postal_code=fake.postalcode()
                            , active=True,
                            currency=currency, payment_method=fake.random_element
    (elements=('Cash', 'Bank transfer', 'Paypal', 'Bitcoins')))

    organization2.save()