from random import randint
from django.utils import timezone
from membership_core.models import SystemCurrency, RenewalPeriod, Service
from membership_manager.models import Contact, Organization, Membership, MembershipRenew, Invoice
from faker import Faker

fake = Faker()

def add_organization():
    currencies_list = list(SystemCurrency.objects.all())
    contacts_list = list(Contact.objects.all())
    organizations_list = []
    for contact in contacts_list:
        currency = currencies_list[randint(0,len(currencies_list)-1)]  # get random currenie instance
        organization = Organization(name=f'{fake.company()} {fake.company_suffix()}',
                                                   initials=fake.pystr(min_chars=4, max_chars=4).upper(),
                                                   contact=contact ,email=fake.email()
                                                   ,cellphone=fake.phone_number(),
                                                   phone=fake.phone_number(), address=fake.address(),
                                                   country=fake.country() ,city=fake.city()
                                                   ,province=fake.city(),
                                                   postal_code=fake.postalcode()
                                                   ,active=True,
                                                   currency=currency, payment_method=fake.random_element
                (elements=('Cash' ,'Bank transfer', 'Paypal', 'Bitcoins')))
        organizations_list.append(organization)
    Organization.objects.bulk_create(organizations_list)

def create_contacts(contacts_num):
    currencies_list = list(SystemCurrency.objects.all())
    contacts_list = []
    for c in range(contacts_num):
        currency = currencies_list[randint(0,len(currencies_list)-1)] # get random currenie instance
        contact = Contact(email=f'test{c}@solvosoft.com' ,first_name=fake.first_name(),
                                         last_name=fake.last_name(), cellphone=fake.phone_number(),
                                         phone=fake.phone_number(), address=fake.address(),
                                         country=fake.country() ,city=fake.city() ,province=fake.city(),
                                         postal_code=fake.postalcode()
                                         ,active=True,
                                         currency=currency, payment_method=fake.random_element(elements=('Cash' ,'Bank transfer', 'Paypal', 'Bitcoins')))
        contacts_list.append(contact)
    Contact.objects.bulk_create(contacts_list)

# CASE ONE #
def generate_graceperiod_memberships():
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id = contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()

    # membresìa con periodo de gracia a vencer hoy
    membership = Membership.objects.create(
        creation_date = now - timezone.timedelta(days=45), #created 45 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD 1',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='graceperiod'
    )
    membership.services.set(list(Service.objects.all())[:3])
    renew = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=45),
        membership=membership,
        start_date=now - timezone.timedelta(days=45),
        end_date=now - timezone.timedelta(days=15),
        graceperiod=False,
        active=True)
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=15),
        membership=membership,
        start_date=now - timezone.timedelta(days=15),
        end_date=now,
        graceperiod=True,
        active=True)
    Invoice.objects.create(
        creation_date = now - timezone.timedelta(days=45),
        expiration_date = now - timezone.timedelta(days=15),
        membership = membership,
        renewal_period = renew,
        description = 'Invoice unit test',
        amount = int(membership.annual_cost) / int(membership.renewal_period.months),
        currency = membership.currency,
        status='pending'
    )

    # membresìa con periodo de gracia a vencer hoy
    memb= Membership.objects.create(
        creation_date = now - timezone.timedelta(days=30), #created 45 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD 2',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='graceperiod'
    )
    memb.services.set(list(Service.objects.all())[:3])
    ren = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        membership=memb,
        start_date=now - timezone.timedelta(days=30),
        end_date=now ,
        graceperiod=False,
        active=True)

    Invoice.objects.create(
        creation_date = now - timezone.timedelta(days=30),
        expiration_date = now ,
        membership = memb,
        renewal_period = ren,
        description = 'Invoice unit test',
        amount = int(memb.annual_cost) / int(memb.renewal_period.months),
        currency = memb.currency,
        status='pending'
    )

    #membresìas con periodo de gracia, con renewals incompletos
    #(Fechas no coinciden y ademàs deberìan de haber dos , uno normal y otro periodo de gracia
    membership1 = Membership.objects.create(
        creation_date = now - timezone.timedelta(days=45), #created 45 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD 3',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='graceperiod'
    )
    membership1.services.set(list(Service.objects.all())[:3])
    renew1 = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        membership=membership1,
        start_date=now - timezone.timedelta(days=20),
        end_date=now,
        graceperiod=False,
        active=True)

    Invoice.objects.create(
        creation_date = now - timezone.timedelta(days=30),
        expiration_date = now,
        membership = membership1,
        renewal_period = renew1,
        description = 'Invoice unit test',
        amount = int(membership1.annual_cost) / int(membership1.renewal_period.months),
        currency = membership1.currency,
        status='pending'
    )
    #membresìa con periodo de gracia sin renews
    tmp_membership = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=30),  # created 30 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD 4',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='graceperiod'
    )
    tmp_membership.services.set(list(Service.objects.all())[:3])

    #
# CASE TWO #
def generate_active_memberships_to_graceperiod():
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id = contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()

    # membresías activas sin periodo de renovación
    tmp_membership = Membership.objects.create(
        creation_date = now, #created 30 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='active'
    )
    tmp_membership.services.set(list(Service.objects.all())[:3])

    # membresías activas con periodo de renovación
    membership1 = Membership.objects.create(
        creation_date = now, #created 15 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership1.services.set(list(Service.objects.all())[:3])
    MembershipRenew.objects.create(
        creation_date=now,
        membership=membership1,
        start_date=now,
        end_date=now + timezone.timedelta(days=30),
        graceperiod=False,
        active=True)

    # membresías activas con periodo de renovaciòn por vencer (activar periodod e gracia)
    membership2 = Membership.objects.create(
        creation_date = now - timezone.timedelta(days=30), #created 30 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership2.services.set(list(Service.objects.all())[:3])

    renew2= MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        membership=membership2,
        start_date=now - timezone.timedelta(days=30),
        end_date=now,
        graceperiod=False,
        active=True)

    Invoice.objects.create(
        creation_date = now - timezone.timedelta(days=30),
        expiration_date = now,
        membership = membership2,
        renewal_period = renew2,
        description = 'Invoice unit test',
        amount = int(membership2.annual_cost) / int(membership2.renewal_period.months),
        currency = membership2.currency,
        status='pending'
    )

    # membresia sin periodo de gracia, pero renewals con periodo de gracia
    membership3 =  Membership.objects.create(
        creation_date = now, #created 30 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership3.services.set(list(Service.objects.all())[:3])

    renew3 = MembershipRenew.objects.create(
        creation_date=now,
        membership=membership3,
        start_date=now,
        end_date=now + timezone.timedelta(days=30),
        graceperiod=True,
        active=True)

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        expiration_date=now,
        membership=membership3,
        renewal_period=renew3,
        description='Invoice unit test',
        amount=int(membership3.annual_cost) / int(membership3.renewal_period.months),
        currency=membership3.currency,
        status='pending'
    )

    #
# CASE THREE #
def generate_inactive_memberships():
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id = contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()

    #Membresías inactivas, con periodos de gracia inactivos y pago pendiente
    membership1 = Membership.objects.create(
        creation_date = now - timezone.timedelta(days=60),
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='inactive'
    )
    membership1.services.set(list(Service.objects.all())[:3])

    renew1 = MembershipRenew.objects.create(
        creation_date = now - timezone.timedelta(days=60),
        membership = membership1,
        start_date = now - timezone.timedelta(days=60),
        end_date= now - timezone.timedelta(days=30),
        graceperiod=False,
        active=False)

    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        membership=membership1,
        start_date=now - timezone.timedelta(days=30),
        end_date=now - timezone.timedelta(days=15),
        graceperiod=True,
        active=False)

    Invoice.objects.create(
        creation_date = now - timezone.timedelta(days=30),
        expiration_date = now,
        membership = membership1,
        renewal_period = renew1,
        description = 'Invoice unit test',
        amount = int(membership1.annual_cost) / int(membership1.renewal_period.months),
        currency = membership1.currency,
        status='pending'
    )

    # Membresìas activas, con periodo de gracia vencido, varios dias
    membership2 =  Membership.objects.create(
        creation_date = now - timezone.timedelta(days=49),
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership2.services.set(list(Service.objects.all())[:3])

    renew2 = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=49),
        membership=membership2,
        start_date=now,
        end_date=now - timezone.timedelta(days=19),
        graceperiod=False,
        active=True)

    MembershipRenew.objects.create(
        creation_date = now - timezone.timedelta(days=19),
        membership=membership2,
        start_date=now - timezone.timedelta(days=19),
        end_date=now - timezone.timedelta(days=4),
        graceperiod=True,
        active=True)

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=19),
        expiration_date=now,
        membership=membership2,
        renewal_period=renew2,
        description='Invoice unit test',
        amount=int(membership2.annual_cost) / int(membership2.renewal_period.months),
        currency=membership2.currency,
        status='pending'
    )


    # Membresìas inactivas sin renewals
    tmp_memb = Membership.objects.create(
        creation_date = now - timezone.timedelta(days=49),
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period= RenewalPeriod.objects.all().first(),
        state='inactive'
    )
    tmp_memb.services.set(list(Service.objects.all())[:3])
    #
# CASE FOUR #
def generate_memberships_to_pay():
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id = contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()

    # membresìa con periodo de gracia a vencer hoy
    membership = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=40),  # created 45 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='graceperiod'
    )
    membership.services.set(list(Service.objects.all())[:3])
    renew = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=40),
        membership=membership,
        start_date=now - timezone.timedelta(days=40),
        end_date=now - timezone.timedelta(days=10),
        graceperiod=False,
        active=True)
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=10),
        membership=membership,
        start_date=now - timezone.timedelta(days=10),
        end_date=now + timezone.timedelta(days=5),
        graceperiod=True,
        active=True)
    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=40),
        expiration_date=now - timezone.timedelta(days=10),
        membership=membership,
        renewal_period=renew,
        description='Invoice unit test',
        amount=int(membership.annual_cost) / int(membership.renewal_period.months),
        currency=membership.currency,
        status='pending'
    )

    # Membresìas inactivas, con periodo de gracia vencido
    membership2 = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=50),  # created 45 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='inactive'
    )
    membership2.services.set(list(Service.objects.all())[:3])
    renew2 = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=50),
        membership=membership2,
        start_date=now - timezone.timedelta(days=50),
        end_date=now - timezone.timedelta(days=20),
        graceperiod=False,
        active=False)
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=20),
        membership=membership2,
        start_date=now - timezone.timedelta(days=20),
        end_date=now - timezone.timedelta(days=5),
        graceperiod=True,
        active=False)
    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=50),
        expiration_date=now - timezone.timedelta(days=20),
        membership=membership2,
        renewal_period=renew2,
        description='Invoice unit test',
        amount=int(membership2.annual_cost) / int(membership2.renewal_period.months),
        currency=membership2.currency,
        status='pending'
    )

    #membresìas activas , no vencidas.
    membership3 = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=25),  # created 25 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership3.services.set(list(Service.objects.all())[:3])
    renew3 = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=25),
        membership=membership2,
        start_date=now - timezone.timedelta(days=25),
        end_date=now + timezone.timedelta(days=5),
        graceperiod=False,
        active=True
    )

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=25),
        expiration_date=now + timezone.timedelta(days=5),
        membership=membership3,
        renewal_period=renew3,
        description='Invoice unit test',
        amount=int(membership3.annual_cost) / int(membership3.renewal_period.months),
        currency=membership3.currency,
        status='pending'
    )
    #membresìas activas , no vencida factura inactiva
    membership4 = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=35),  # created 25 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership4.services.set(list(Service.objects.all())[:3])
    renew4 = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=35),
        membership=membership4,
        start_date=now - timezone.timedelta(days=35),
        end_date=now - timezone.timedelta(days=5),
        graceperiod=False,
        active=False
    )

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=35),
        expiration_date=now + timezone.timedelta(days=5),
        membership=membership4,
        renewal_period=renew4,
        description='Invoice unit test',
        amount=int(membership4.annual_cost) / int(membership4.renewal_period.months),
        currency=membership4.currency,
        status='inactive'
    )


# NOTIFICATION SCENARIOS #

# CASAE  - NOTIFY FOR INVOICE CREATION
def generate_memberships_to_notify_expiration_create_invoice():
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id = contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()

    # Membresìas en plazo de 60 dias por vencer (creacion de invoice) por vencer.
    membership = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=5),  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership.services.set(list(Service.objects.all())[:3])
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=5),
        membership=membership,
        start_date=now - timezone.timedelta(days=5),
        end_date=now + timezone.timedelta(days=50),
        graceperiod=False,
        active=True)

    # Membresìas en plazo de 60 dias por vencer (creacion de invoice) por vencer.
    membership2 = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=5),  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership2.services.set(list(Service.objects.all())[:3])
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=5),
        membership=membership2,
        start_date=now - timezone.timedelta(days=5),
        end_date=now + timezone.timedelta(days=10),
        graceperiod=False,
        active=True)

# CASE - NOTIFY FOR EXPIRATION TIMES "
def generate_memberships_to_notify_expiration():
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id=contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()

    # Membresìas en plazo de 30 dias por vencer (creacion de invoice) por vencer.
    membership = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=30),  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership.services.set(list(Service.objects.all())[:3])
    renew = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        membership=membership,
        start_date=now - timezone.timedelta(days=30),
        end_date=now + timezone.timedelta(days=30),
        graceperiod=False,
        active=True)

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        expiration_date=now + timezone.timedelta(days=30),
        membership=membership,
        renewal_period=renew,
        description='Invoice unit test',
        amount=int(membership.annual_cost) / int(membership.renewal_period.months),
        currency=membership.currency,
        status='pending'
    )

    # Membresìas en plazo de 15 dias por vencer (creacion de invoice) por vencer.
    membership2 = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=15),  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership2.services.set(list(Service.objects.all())[:3])
    renew2 = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=15),
        membership=membership2,
        start_date=now - timezone.timedelta(days=15),
        end_date=now + timezone.timedelta(days=15),
        graceperiod=False,
        active=True)

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=15),
        expiration_date=now + timezone.timedelta(days=15),
        membership=membership2,
        renewal_period=renew2,
        description='Invoice unit test',
        amount=int(membership2.annual_cost) / int(membership2.renewal_period.months),
        currency=membership2.currency,
        status='pending'
    )

    # Membresìas en plazo de 1 dias por vencer (creacion de invoice) por vencer.
    membership3 = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=23),  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership3.services.set(list(Service.objects.all())[:3])
    renew3 = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=23),
        membership=membership3,
        start_date=now - timezone.timedelta(days=23),
        end_date=now + timezone.timedelta(days=7),
        graceperiod=False,
        active=True)

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=23),
        expiration_date=now + timezone.timedelta(days=7),
        membership=membership3,
        renewal_period=renew3,
        description='Invoice unit test',
        amount=int(membership3.annual_cost) / int(membership3.renewal_period.months),
        currency=membership3.currency,
        status='pending'
    )

    # Membresìas en plazo de 7 dias por vencer (creacion de invoice) por vencer.
    membership4 = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=29),  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='active'
    )
    membership4.services.set(list(Service.objects.all())[:3])
    renew4 = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=29),
        membership=membership4,
        start_date=now - timezone.timedelta(days=29),
        end_date=now + timezone.timedelta(days=1),
        graceperiod=False,
        active=True)

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=29),
        expiration_date=now + timezone.timedelta(days=1),
        membership=membership4,
        renewal_period=renew4,
        description='Invoice unit test',
        amount=int(membership4.annual_cost) / int(membership4.renewal_period.months),
        currency=membership4.currency,
        status='pending'
    )
# CASE - NOTIFY FOR INACTIVE MEMBERSHIP ·
def generate_memberships_to_deactivate():
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id=contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()
    # Membresìas vencida,
    membership = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=45),  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='graceperiod'
    )
    membership.services.set(list(Service.objects.all())[:3])
    renew = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=45),
        membership=membership,
        start_date=now - timezone.timedelta(days=45),
        end_date=now - timezone.timedelta(days=15),
        graceperiod=False,
        active=True)

    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=15),
        membership=membership,
        start_date=now - timezone.timedelta(days=15),
        end_date=now,
        graceperiod=True,
        active=True)

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=45),
        expiration_date=now - timezone.timedelta(days=15),
        membership=membership,
        renewal_period=renew,
        description='Invoice unit test',
        amount=int(membership.annual_cost) / int(membership.renewal_period.months),
        currency=membership.currency,
        status='pending'
    )
# CASE - NOTIFY FOR GRACEPERIOD ADDED TO MEMBERSHIP ·
def generate_memberships_to_notify_graceperiod():
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id=contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()

    # Membresìas vencida,
    membership = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=30),  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} STANDARD',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='graceperiod'
    )
    membership.services.set(list(Service.objects.all())[:3])
    renew = MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        membership=membership,
        start_date=now - timezone.timedelta(days=30),
        end_date=now,
        graceperiod=False,
        active=True)

    Invoice.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        expiration_date=now,
        membership=membership,
        renewal_period=renew,
        description='Invoice unit test',
        amount=int(membership.annual_cost) / int(membership.renewal_period.months),
        currency=membership.currency,
        status='pending'
    )

