from random import random

from membership_manager.models import Contact

currencies_list = list(SystemCurrency.object.all())


def add_organization(self):
    self.contact_qset = Contact.objects.filter(pk__in = self.contacts_ids)
    for contact in self.contact_qset:
        currency = currencies_list[random.randint(len(currencies_list) - 1)]  # get random currenie instance
        organization = Organization.objects.create(name=f'{self.fake.company()} {self.fake.company_suffix()}',
                                                   initials=self.fake.pystr(min_chars=4, max_chars=4).upper(),
                                                   contact=contact ,email=self.fake.email()
                                                   ,cellphone=self.fake.phone_number(),
                                                   phone=self.fake.phone_number(), address=self.fake.address(),
                                                   country=self.fake.country() ,city=self.fake.city()
                                                   ,province=self.fake.city(),
                                                   postal_code=self.fake.postalcode()
                                                   ,active=self.fake.boolean(chance_of_getting_true=99),
                                                   currency=currency, payment_method=self.fake.random_element
                (elements=('Cash' ,'Bank transfer', 'Paypal', 'Bitcoins')))

def create_contacts(self):
    for c in range(self.contacts_num):
        currency = currencies_list[random.randint(len(currencies_list)-1)] # get random currenie instance
        contact = Contact.objects.create(email=self.fake.email() ,first_name=self.fake.first_name(),
                                         last_name=self.fake.last_name(), cellphone=self.fake.phone_number(),
                                         phone=self.fake.phone_number(), address=self.fake.address(),
                                         country=self.fake.country() ,city=self.fake.city() ,province=self.fake.city(),
                                         postal_code=self.fake.postalcode()
                                         ,active=self.fake.boolean(chance_of_getting_true=99),
                                         currency=currency, payment_method=self.fake.random_element
                (elements=('Cash' ,'Bank transfer', 'Paypal', 'Bitcoins')))
        self.contacts_ids.append(contact.pk)
    self.add_organization()