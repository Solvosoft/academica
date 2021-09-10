from django.contrib.auth.models import User, Permission
from django.core.management import BaseCommand
from django.utils.timezone import now

from matricula.models import Category, Course, Period, Group, Student, Enroll
from membership_core.models import Country


def get_enroll(group, user, student):

    enroll = Enroll.objects.create(
        enroll_finished = True,
        enroll_activate = True,
        group = group,
        student = student,
        course_status = "approved")
    return enroll


def generate_scenarius():
    cat, created = Category.objects.get_or_create(name='cat1', description='cat1')
    c1 = Course.objects.create(category=cat, name='course1', content='course1')
    c2 = Course.objects.create(category=cat, name='course2', content='course2')
    c3 = Course.objects.create(category=cat, name='course3', content='course3')
    c4 = Course.objects.create(category=cat, name='course4', content='course4')
    period1 = Period.objects.create(name='per1', start_date=now(), finish_date=now())
    period2 = Period.objects.create(name='per2', start_date='2026-10-10', finish_date='2027-10-10')
    period3 = Period.objects.create(name='per3', start_date='2010-11-11', finish_date='2011-11-11')

    c1g1 = Group.objects.create(
        period = period1,
        course = c1,
        name = 'g1',
        schedule = 'Nothing',
        pre_enroll_start = now(),
        pre_enroll_finish = now(),
        enroll_start = now(),
        enroll_finish = now(),
        cost = 0,
        maximum = 200,
        is_open = True,
        flow = 0)

    c1g2 = Group.objects.create(
        period = period1,
        course = c1,
        name = 'g2',
        schedule = 'Nothing',
        pre_enroll_start = now(),
        pre_enroll_finish = now(),
        enroll_start = now(),
        enroll_finish = now(),
        cost = 0,
        maximum = 200,
        is_open = True,
        flow = 0)

    c2g1 = Group.objects.create(
            period = period2,
            course = c2,
            name = 'g1',
            schedule = 'Nothing',
            pre_enroll_start = now(),
            pre_enroll_finish = now(),
            enroll_start = now(),
            enroll_finish = now(),
            cost = 0,
            maximum = 200,
            is_open = True,
            flow = 0)

    c3g1 = Group.objects.create(
        period=period2,
        course=c3,
        name='g1',
        schedule='Nothing',
        pre_enroll_start=now(),
        pre_enroll_finish=now(),
        enroll_start=now(),
        enroll_finish=now(),
        cost=0,
        maximum=200,
        is_open=True,
        flow=0)

    c4g1 = Group.objects.create(
        period=period2,
        course=c4,
        name='g1',
        schedule='Nothing',
        pre_enroll_start=now(),
        pre_enroll_finish=now(),
        enroll_start=now(),
        enroll_finish=now(),
        cost=0,
        maximum=200,
        is_open=True,
        flow=0)

    c4g2 = Group.objects.create(
        period=period3,
        course=c4,
        name='g2',
        schedule='Nothing',
        pre_enroll_start=now(),
        pre_enroll_finish=now(),
        enroll_start=now(),
        enroll_finish=now(),
        cost=0,
        maximum=200,
        is_open=True,
        flow=0)

    groups = [c1g1, c1g2, c2g1, c3g1, c4g1, c4g2]

    '''
    user1 = User.objects.create_user(username='nombre1',
                                         email='prueba1@gmail.com',
                                         password='password1')

    user2 = User.objects.create_user(username='nombre2',
                                     email='prueba2@gmail.com',
                                     password='password2')

    user3 = User.objects.create_user(username='nombre3',
                                     email='prueba3@gmail.com',
                                     password='password3')
    '''
    user1 = User.objects.get(username='nombre1')
    user2 = User.objects.get(username='nombre2')
    user3 = User.objects.get(username='nombre3')

    country1 = Country.objects.create(name='Costa Rica', flag='cr', code='CR')
    country2 = Country.objects.create(name='Afganistán', flag='af', code='AF')
    country3 = Country.objects.create(name='Australia', flag='au', code='AU')

    student1 = Student.objects.create(
        user=user1,
        organization='org',
        country=country1,
        city='CR',
        phone_number='88888888',
        expired_at=now()
    )

    student2 = Student.objects.create(
        user=user2,
        organization='org',
        country=country2,
        city='AF',
        phone_number='88888888',
        expired_at=now()
    )

    student3 = Student.objects.create(
        user=user3,
        organization='org',
        country=country3,
        city='AU',
        phone_number='88888888',
        expired_at=now()
    )

    enroll1 = get_enroll(groups[0], user1, student1)
    enroll1.go_to_one_class = False
    enroll1.course_status = "uncomplete"

    enroll2 = get_enroll(groups[1], user1, student1)
    enroll2.go_to_one_class = True
    enroll2.course_status = "reproved"

    enroll3 = get_enroll(groups[2], user3, student3)
    enroll3.go_to_one_class = False
    enroll3.course_status = "approved"

    enroll4 = get_enroll(groups[3], user1, student1)
    enroll4.go_to_one_class = True
    enroll4.course_status = "uncomplete"

    enroll5 = get_enroll(groups[4], user2, student2)
    enroll5.go_to_one_class = True
    enroll5.course_status = "uncomplete"

    enroll6 = get_enroll(groups[5], user2, student2)
    enroll6.go_to_one_class = True
    enroll6.course_status = "uncomplete"

    enroll1.save()
    enroll2.save()
    enroll3.save()
    enroll4.save()
    enroll5.save()
    enroll6.save()


class Command(BaseCommand):
    help = "Create objects to db (Postgresql)"

    def handle(self, *args, **options):
        generate_scenarius()