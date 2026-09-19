from matricula.tests.utils import login_report_admin
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now

from matricula.models import Category, Course, Period, Group, Enroll, Student
from membership_core.models import SystemCurrency, Country


class NeverAttendStudentsTestCase(TestCase):

    user_count=1

    def setUp(self):
        self.client = Client()
        login_report_admin(self.client)
        self.url = reverse('student_without_lessons_report-list')
        self.generate_scenarius()

    def get_enroll(self, group):
        user = User.objects.create_user(username='user%d'%self.user_count,
                                 email='luis%d@upo.com'%self.user_count,
                                 password='password')
        self.user_count+=1

        country, created =Country.objects.get_or_create(code='CRC', defaults={'name': 'Costa Rica'})
        student = Student.objects.create(
            user=user,
            organization='org',
            country=country,
            city='CR',
            phone_number='88888888',
            expired_at=now()
        )

        enroll = Enroll.objects.create(
            enroll_finished=True,
            enroll_activate=True,
            group=group,
            student=student,
            course_status="uncompleted")
        return enroll


    def generate_scenarius(self):
        cat = Category.objects.create(name='cat1', description='cat1')
        c1 = Course.objects.create(category=cat, name='course1', content='course1')
        c2 = Course.objects.create(category=cat, name='course2', content='course2')
        c3 = Course.objects.create(category=cat, name='course3', content='course3')
        period = Period.objects.create(name='per1', start_date=now(), finish_date=now())

        c1g1 = Group.objects.create(
            period=period,
            course=c1,
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

        c2g1 = Group.objects.create(
            period=period,
            course=c2,
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

        c3g1 = Group.objects.create(
            period=period,
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


        Country.objects.get_or_create(code='CRC', defaults={'name': 'Costa Rica'})

        groups = [c1g1, c2g1, c3g1]

        for x in range(10):
            enroll = self.get_enroll(groups[x % 3])
            enroll.go_to_one_class = False
            enroll.save()

        # c1g1: 4 , c2g1: 3, c3g1: 3



    def test_graph_data(self):
        response = self.client.get(self.url)

        data = response.json()['data']
        dataset = data['datasets']

        self.assertEqual(dataset[0]['data'], [4])
        self.assertEqual(dataset[1]['data'], [3])
        self.assertEqual(dataset[2]['data'], [3])


    def test_graph_type(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['type'], 'bar')
