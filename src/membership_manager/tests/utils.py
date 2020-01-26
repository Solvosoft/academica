from random import randint
from django.utils import timezone
from membership_core.models import SystemCurrency, RenewalPeriod, ServiceType
from membership_manager.models import Contact, Organization, Membership, MembershipRenew, Invoice
from faker import Faker

fake = Faker()

def add_organization():
    """
        This method create a organizations for te created contacts
        :return nothing:
    """
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
    """
        This method create a contacts

        arg:
             contacts_num : contacts quantity.
        :return nothing:
    """
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

# CASE - NOTIFY FOR GRACEPERIOD ADDED TO MEMBERSHIP ·
def generate_memberships_to_notify_graceperiod():
    """
        This method create a specific scenario using expired memberships, to test membership renew to graceperiod notifications
        :return nothing:
    """
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id=contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()

    #Membresìas vencida,
    membership = Membership.objects.create(
        creation_date=now - timezone.timedelta(days=30),  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name} NOT_GRACEP_1',
        annual_cost=550,
        currency=currencies_list[randint(0,len(currencies_list)-1)],  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=RenewalPeriod.objects.all().first(),
        state='graceperiod'
    )
    membership.services.set(list(ServiceType.objects.all())[:3])

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
        amount=int(membership.annual_cost) * int(membership.renewal_period.months),
        currency=membership.currency,
        status='pending')

#····· TEST MEMBERSHIP BUILDER ·····#
def generate_test_membership(*args, **kwargs):
    dev = {}
    now = timezone.now()
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id=contact.id).order_by('?').first()
    currency = SystemCurrency.objects.all().order_by('?').first()
    renew_period = kwargs.get('renewal_period', RenewalPeriod.objects.all().first())
    build_renewal =  kwargs.get('build_renewal', False)
    build_invoice = kwargs.get('build_invoice', False)
    membership = Membership.objects.create(
        creation_date=kwargs.get('creation_date', now - timezone.timedelta(days=30)) ,  # created 5 days ago
        membership_type='Organizacional',
        contact=contact, organization=organization, name=f'{organization.name}',
        annual_cost=kwargs.get('annual_cost', 550),
        currency=kwargs.get('currency', currency),  # get random currenie instance
        description=fake.paragraph(nb_sentences=10, variable_nb_sentences=True, ext_word_list=None),
        renewal_period=renew_period,
        state=kwargs.get('state','active')
    )
    membership.services.set(list(ServiceType.objects.all())[:3])
    dev['membership'] = membership
    if build_renewal:
        renew = MembershipRenew.objects.create(
            creation_date=kwargs.get('creation_date', now - timezone.timedelta(days=30)),
            membership=membership,
            start_date=kwargs.get('start_date', now - timezone.timedelta(days=30)),
            end_date=kwargs.get('end_date', now),
            graceperiod=kwargs.get('graceperiod', False),
            active=kwargs.get('active', True) )
        dev['renew'] = renew

    if build_invoice:
        invoice = Invoice.objects.create(
            creation_date=kwargs.get('creation_date', now - timezone.timedelta(days=30)),
            expiration_date=kwargs.get('expiration_date',now),
            membership=membership,
            renewal_period=renew,
            description='Invoice unit test',
            amount=int(membership.annual_cost) * int(membership.renewal_period.months),
            currency=membership.currency,
            status=kwargs.get('status','pending'))
        dev['invoice'] = invoice

    return dev
# TEST SCENARIO - test_memberships.py
def generate_membershib_to_inactive():
    now = timezone.now()
    # It will be inactive
    mem1 = generate_test_membership(
        build_renewal= True, graceperiod=True, state="graceperiod",
        build_invoice= True)

    # Also inactive yesterday
    mem2 = generate_test_membership(
        build_renewal = True, state="graceperiod",  graceperiod=True,
        end_date=now - timezone.timedelta(days=1), build_invoice= True)

    # Not inactive, one day is need it.
    mem3 = generate_test_membership(
        build_renewal= True, graceperiod=True, state="graceperiod",
        end_date=now + timezone.timedelta(days=1), build_invoice= True)
    return [mem1, mem2, mem3]

def generate_membership_to_graceperiod():
    now = timezone.now()
    # Active to graceperiod today
    mem1 = generate_test_membership(
        build_renewal=True, state="active",
        build_invoice=True)

    # Also active , one day is need it, to graceperiod.
    mem2 = generate_test_membership(
        build_renewal=True, state="active",
        end_date=now + timezone.timedelta(days=1), build_invoice=True)

    #active, end yesterday.
    mem3 = generate_test_membership(
        build_renewal=True, state="active",
        end_date=now - timezone.timedelta(days=1),expiration_date = now - timezone.timedelta(days=1)
        , build_invoice=True)
    return [mem1, mem2, mem3]

def generate_membership_to_create_invoice():
    now = timezone.now()
    # Active end today , without invoice
    mem1 = generate_test_membership(
        build_renewal=True, state="active",
        )
    # Active end in 30 days, without invoice
    mem2 = generate_test_membership(
        build_renewal=True, state="active",
        end_date=now + timezone.timedelta(days=30))
    #active, end in 30 days with invoice.
    mem3 = generate_test_membership(
        build_renewal=True, state="active",creation_date=now,
        end_date=now + timezone.timedelta(days=30),expiration_date = now + timezone.timedelta(days=30)
        , build_invoice=True)
    return [mem1, mem2, mem3]

def generate_memberships_active_with_inconsistent_features():
    """
        This method create a specific scenario using active  memberships with inconsistent_features,
         next to (change to grace period, create invoice or deactivate) the membership.
        :return nothing:
    """
    now = timezone.now()
    dev = {}
    # membresías activa sin periodo de renovación
    mem1 = generate_test_membership(creation_date = now,
        state="active",
    )
    dev['membership_active_without_renewal'] = mem1
    # membresia activa con periodo de renovación en periodo de gracia
    mem2 = generate_test_membership(creation_date=now,
        state="active",build_renewal=True,
        graceperiod=True,start_date=now, end_date=now+timezone.timedelta(days=30)
    )
    dev['membership_active_with_renewal_on_graceperiod'] = mem2
    # membresia activa con periodo de renovación en periodo de gracia
    mem3 = generate_test_membership(
        state="active",build_renewal=True,
        graceperiod=True, end_date=now,
        build_invoice=True, expiration_date=now
    )
    dev['membership_active_with_renewal_invoice_on_graceperiod'] = mem3

# TEST SCENARIO - tests_memberships_graceperiod.py
def generate_memberships_graceperiod_to_inactive_and_active_to_graceperiod():
    """
        This method create a specific scenario using memberships on graceperiod,
         or memberships to change in future to graceperiod
        :return nothing:
    """
    now = timezone.now()
    dev = {}
    # membresía con periodo de gracia vencida (to deactivate)
    mem1 = generate_test_membership(creation_date = now - timezone.timedelta(days=60),
        state='graceperiod',start_date=now - timezone.timedelta(days=60),
        end_date=now - timezone.timedelta(days=30),graceperiod=False,
        active=True,expiration_date = now - timezone.timedelta(days=30),status='pending',
        build_invoice=True,build_renewal=True
    )
    dev['membership_graceperiod_expired'] = mem1
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        membership=mem1['membership'],
        start_date=now - timezone.timedelta(days=30),
        end_date=now - timezone.timedelta(days=15),
        graceperiod=True,
        active=True)

    # membresìa con periodo de gracia a vencer hoy (to deactivate)
    mem2 = generate_test_membership(creation_date = now - timezone.timedelta(days=45),
        state='graceperiod',start_date=now - timezone.timedelta(days=45),
        end_date=now - timezone.timedelta(days=15), graceperiod=False,
        active=True, expiration_date = now - timezone.timedelta(days=15), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_graceperiod_expire_today'] = mem2
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=15),
        membership=mem2['membership'],
        start_date=now - timezone.timedelta(days=15),
        end_date=now,
        graceperiod=True,
        active=True)

    #membresìas con periodo de gracia, con renewals incompletos
    #(Fechas no coinciden y ademàs deberìan de haber dos , uno normal y otro periodo de gracia)
    # NO SE TOMA EN CUENTA solo para realizar pago
    mem3 = generate_test_membership( creation_date = now - timezone.timedelta(days=45),
        state='graceperiod',start_date=now - timezone.timedelta(days=20),
        end_date=now, graceperiod=False,
        active=True,  expiration_date = now, status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_graceperiod_incomplete_renewals'] = mem3

    #membresìas con periodo de gracia, no realiza nada, ya que está a espera de vencerse
    mem4 = generate_test_membership( creation_date = now - timezone.timedelta(days=45),
        state='graceperiod',start_date=now - timezone.timedelta(days=30),
        end_date=now, graceperiod=False,
        active=True,  expiration_date = now, status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_graceperiod_regular'] = mem4
    MembershipRenew.objects.create(
        creation_date=now,
        membership=mem4['membership'],
        start_date=now,
        end_date=now + timezone.timedelta(days=15),
        graceperiod=True,
        active=True)

    #membresìa con periodo de gracia sin renews, creada hace 30 días
    mem5 = generate_test_membership(creation_date=now - timezone.timedelta(days=30),
        state='graceperiod'
    )
    dev['membership_graceperiod_without_renewals'] = mem5
    #membresìa con periodo de gracia sin invoice, creada hace 30 días
    mem6 = generate_test_membership(creation_date = now - timezone.timedelta(days=30),
        state='graceperiod',start_date=now - timezone.timedelta(days=30),
        end_date=now, graceperiod=False, active=True, build_renewal=True
    )
    dev['membership_graceperiod_without_invoice'] = mem6

    # membresía activa ( para cambiar a graceperiod)
    mem7 = generate_test_membership(creation_date=now - timezone.timedelta(days=30),
                                    state='active', start_date=now - timezone.timedelta(days=30),
                                    end_date=now, graceperiod=False,
                                    active=True, expiration_date=now, status='pending',
                                    build_invoice=True, build_renewal=True
                                    )
    dev['membership_active_expire_today'] = mem7

    # membresía activa ( para cambiar a graceperiod) sin invoice
    mem8 = generate_test_membership(creation_date=now - timezone.timedelta(days=30),
        state='active', start_date=now - timezone.timedelta(days=30),
        end_date=now, graceperiod=False,
        active=True, build_renewal=True
    )
    dev['membership_active_expire_today_without_invoice'] = mem8

    # membresía activa ( para cambiar a graceperiod) sin invoice
    mem9 = generate_test_membership(creation_date=now - timezone.timedelta(days=31),
        state='active', start_date=now - timezone.timedelta(days=31),
        end_date=now - timezone.timedelta(days=1), graceperiod=False,
        active=True, build_renewal=True
    )
    dev['membership_active_expire_yesterday_without_invoice'] = mem9

    return dev
# TEST SCENARIO - tests_memberships_graceperiod.py
def generate_memberships_to_notify_expiration():
    """
        This method create a specific scenario using memberships expiriration, to test invoice expiration notifications
        :return nothing:
    """

    now = timezone.now()
    dev = {}
    # Membresìas en plazo de 30 dias por vencer
    mem1 = generate_test_membership(creation_date=now - timezone.timedelta(days=30),
        state='active',start_date=now - timezone.timedelta(days=30),
        end_date=now + timezone.timedelta(days=30),
        active=True, expiration_date=now + timezone.timedelta(days=30),status='pending',
        build_invoice=True,build_renewal=True
    )
    dev['membership_30_days_to_expire'] = mem1

    # Membresìas en plazo de 15 dias por vencer
    mem2 = generate_test_membership(creation_date=now - timezone.timedelta(days=15),
        state='active',  start_date=now - timezone.timedelta(days=15),
        end_date=now + timezone.timedelta(days=15),
        active=True, expiration_date=now + timezone.timedelta(days=15), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_15_days_to_expire'] = mem2

    # Membresìas en plazo de 7 dias por vencer
    mem3 = generate_test_membership(creation_date=now - timezone.timedelta(days=23),
        state='active', start_date=now - timezone.timedelta(days=23),
        end_date=now + timezone.timedelta(days=7),
        active=True, expiration_date=now + timezone.timedelta(days=7), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_7_days_to_expire'] = mem3

    # Membresìas en plazo de 1 dias por vencer (.
    mem4 = generate_test_membership(state='active', start_date=now - timezone.timedelta(days=30),
        end_date=now + timezone.timedelta(days=1),
        active=True,  expiration_date=now + timezone.timedelta(days=1), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_1_day_to_expire'] = mem4

    # Membresìas en plazo de 60 dias por vencer
    mem5 = generate_test_membership(state='active', start_date=now ,
        end_date=now + timezone.timedelta(days=60),
        active=True,  expiration_date=now + timezone.timedelta(days=60), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_60_days_to_expire'] = mem5
    # Membresìas en plazo de 70 dias por vencer
    mem6 = generate_test_membership(state='active', start_date=now ,
        end_date=now + timezone.timedelta(days=70),
        active=True,  expiration_date=now + timezone.timedelta(days=70), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_70_days_to_expire'] = mem6

    # Membresìas vencida periodo de prueba
    mem7 = generate_test_membership(state='graceperiod', start_date=now - timezone.timedelta(days=30),
                                    end_date=now - timezone.timedelta(days=1),
                                    active=True, expiration_date=now - timezone.timedelta(days=1), status='pending',
                                    build_invoice=True, build_renewal=True
                                    )
    dev['membership_expired_yesterday'] = mem7
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=30),
        membership=mem6['membership'],
        start_date=now - timezone.timedelta(days=30),
        end_date=now + timezone.timedelta(days=15),
        graceperiod=True,
        active=True)

    return dev
# TEST SCENARIO - test_memberships_inactives.py
def generate_memberships_to_deactivate():
    """
        This method create a specific scenario using expired memberships, to test invoice deactivating notifications
        :return nothing:
    """
    now = timezone.now()
    dev = {}
    # Membresía vencida, periodo de prueba
    mem1 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=45),
        state='graceperiod', start_date=now - timezone.timedelta(days=45),
        end_date=now - timezone.timedelta(days=15),
        active=True, expiration_date=now - timezone.timedelta(days=15), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_expired'] = mem1
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=15),
        membership=mem1['membership'],
        start_date=now - timezone.timedelta(days=15),
        end_date=now,
        graceperiod=True,
        active=True)

    # Membresìas no vencida
    mem2 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=40),
        state='graceperiod', start_date=now - timezone.timedelta(days=40),
        end_date=now - timezone.timedelta(days=10),
        active=True, expiration_date=now - timezone.timedelta(days=10), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_graceperiod_active'] = mem2
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=10),
        membership=mem2['membership'],
        start_date=now - timezone.timedelta(days=10),
        end_date=now + timezone.timedelta(days=5) ,
        graceperiod=True,
        active=True)

    # Membresìas vencida ayer
    mem3 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=45),
        state='graceperiod', start_date=now - timezone.timedelta(days=45),
        end_date=now - timezone.timedelta(days=15),
        active=True, expiration_date=now - timezone.timedelta(days=15), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_expired_yesterday'] = mem3
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=15),
        membership=mem3['membership'],
        start_date=now - timezone.timedelta(days=15),
        end_date=now - timezone.timedelta(days=1),
        graceperiod=True,
        active=True)

    # Membresìas a activar periodo de gracia
    mem4 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=45),
        state='graceperiod', start_date=now - timezone.timedelta(days=45),
        end_date=now - timezone.timedelta(days=15),
        active=True, graceperiod=True,expiration_date=now - timezone.timedelta(days=15), status='pending',
        build_invoice=True, build_renewal=True
    )
    dev['membership_expired_with_one_renewal'] = mem4
    return dev
# TEST SCENARIO - test_memberships_invoice_creation.py
def generate_memberships_to_notify_expiration_create_invoice():
    """
    This method create a specific scenario using memberships to expire, to thest invoice createment notifications
    :return nothing:
    """
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id = contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()
    dev = {}
    # Membresìas en plazo de 60 dias por vencer (creacion de invoice) por vencer.
    mem1 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=5),
        state='active', start_date=now - timezone.timedelta(days=5),
        end_date=now + timezone.timedelta(days=50),
        active=True, status='pending', build_renewal=True
    )
    dev['membership_invoice_create_60days'] = mem1


    # Membresìas en plazo de 30 dias por vencer (creacion de invoice) por vencer.
    mem2 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=5),
        state='active',  start_date=now - timezone.timedelta(days=5),
        end_date=now + timezone.timedelta(days=25),
        active=True, status='pending', build_renewal=True
    )
    dev['membership_invoice_create_30days'] = mem2

    # Membresìas en plazo de 110 dias por vencer (creacion de invoice) por vencer.
    mem3 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=5),
        state='active', start_date=now - timezone.timedelta(days=5),
        end_date=now + timezone.timedelta(days=105),
        active=True, status='pending', build_renewal=True
    )
    dev['membership_invoice_create_110days'] = mem3

    # Membresías en plazo de 30 días con invocie creada
    mem4 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=5),
        state='active', start_date=now - timezone.timedelta(days=5),
        end_date=now + timezone.timedelta(days=25),
        active=True,build_invoice=True,expiration_date=now + timezone.timedelta(days=25),
        status='pending', build_renewal=True
    )
    dev['membership_invoice_create_30days_with_invoice'] = mem4

    # Membresías vencida ayer sin invoice
    mem5 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=31),
        state='active', start_date=now - timezone.timedelta(days=31),
        end_date=now - timezone.timedelta(days=1),
        active=True,
        status='pending', build_renewal=True
    )
    dev['membership_invoice_create_expired_without_invoice'] = mem5
    return dev
# TEST SCENARIO - test_memberships_to_pay.py
def generate_memberships_to_pay():
    """
        This method create a specific scenario for emberships to pay,

        :return nothing:
    """
    contact = Contact.objects.all().order_by('?').first()
    organization = Organization.objects.filter(contact_id = contact.id).order_by('?').first()
    currencies_list = list(SystemCurrency.objects.all())
    now = timezone.now()
    dev = {}
    # membresìa con periodo de gracia a vencer hoy
    mem1 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=40),
        state='graceperiod', start_date=now - timezone.timedelta(days=40),
        end_date=now - timezone.timedelta(days=10),
        build_invoice=True,expiration_date=now - timezone.timedelta(days=10),
        active=True, status='pending', build_renewal=True
    )
    dev['membership_to_pay_graceperiod_expire_today'] = mem1
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=10),
        membership=mem1['membership'],
        start_date=now - timezone.timedelta(days=10),
        end_date=now,
        graceperiod=True,
        active=True)
    # Membresìa , con periodo de gracia vencido
    mem2 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=50),
        state='inactive', start_date=now - timezone.timedelta(days=50),
        end_date=now - timezone.timedelta(days=20),
        build_invoice=True,expiration_date=now - timezone.timedelta(days=20),
        active=False, status='pending', build_renewal=True
    )
    dev['membership_to_pay_graceperiod_expired_inactive'] = mem2
    MembershipRenew.objects.create(
        creation_date=now - timezone.timedelta(days=20),
        membership=mem2['membership'],
        start_date=now - timezone.timedelta(days=20),
        end_date=now - timezone.timedelta(days=5),
        graceperiod=True,
        active=False)

    #membresìas activas , no vencidas.
    mem3 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=25),
        state='active', start_date=now - timezone.timedelta(days=25),
        end_date=now + timezone.timedelta(days=5),
        build_invoice=True, expiration_date=now + timezone.timedelta(days=5),
        active=True, status='pending', build_renewal=True
    )
    dev['membership_to_pay_active'] = mem3
    #membresìas inactiva , no vencida factura pendiente
    mem5 = generate_test_membership(
        creation_date=now - timezone.timedelta(days=25),
        state='inactive', start_date=now - timezone.timedelta(days=25),
        end_date=now + timezone.timedelta(days=5),
        build_invoice=True, expiration_date=now + timezone.timedelta(days=5),
        active=False, status='pending', build_renewal=True
    )
    dev['membership_to_pay_inactive'] = mem5

    return dev

