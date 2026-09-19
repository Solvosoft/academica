from matricula.tests.utils import login_report_admin
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now

from matricula.models import Category, Course, Period, Group, Enroll, Student
from membership_core.models import SystemCurrency, Country


class ListReportsTestCase(TestCase):
    user_count=1

    def get_enroll(self, group):
        user = User.objects.create_user(username='user%d'%self.user_count,
                                 email='jacob%d@upo.com'%self.user_count,
                                 password='password')
        self.user_count+=1
        country, created =Country.objects.get_or_create(code='CRC', defaults={'name': 'Costa Rica'})
        student = Student.objects.create(
            user =  user,
            organization = 'org',
            country = country,
            city = 'CR',
            phone_number = '88888888',
            expired_at = now()
        )


        enroll = Enroll.objects.create(
            enroll_finished = True,
            enroll_activate = True,
            group = group,
            student = student,
            course_status = "approved")
        return enroll


    def generate_scenarius(self):
        cat = Category.objects.create(name='cat1', description='cat1')
        c1=Course.objects.create(category=cat, name='course1', content='course1')
        c2=Course.objects.create(category=cat, name='course2', content='course2')
        period = Period.objects.create(name='per1', start_date=now(), finish_date=now())


        c1g1=Group.objects.create(
                period = period,
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

        c1g2=Group.objects.create(
                period = period,
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

        c2g1=Group.objects.create(
                period = period,
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

        groups=[c1g1, c1g2, c2g1]
        for x in range(10):
            enroll = self.get_enroll(groups[x%3])
            if x%4 == 0:
                enroll.go_to_one_class = False
            if x == 7:
                enroll.course_status = "uncompleted"

            if x%3==0:
                enroll.course_status = "reproved"
                # enroll_finished
                # course_status
                # go_to_one_class
            if x == 0:
                enroll.go_to_one_class = True
                enroll.course_status = "approved"
            enroll.save()

        #  0 1 2 5 7 approved
        #  4 8       withoutlessons
        #  7         uncomplete
        #  3 6  9    reproved

        #  C1 0 1 3 4 6 7 9        3 approved 3 reproved 1 uncomplete  1 withoutlessons
        #  C2 2  5  8              2 approved 0 reproved 0 uncomplete  1 withoutlessons



    def setUp(self):
        self.client = Client()
        login_report_admin(self.client)
        self.user = User.objects.create_user(username='jacob1',
                                        email='jacob1@…',
                                        password='password')
        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()
        self.user.user_permissions.add(view_reports)
        self.url = reverse('consolidadoestcurso-list')
        self.generate_scenarius()


    def test_graph_data(self):
        response = self.client.get(self.url)

        data = response.json()['data']
        dataset = data['datasets']
        #  0 1 2 5 7 approved
        #  4 8       withoutlessons
        #  7         uncomplete
        #  3 6  9    reproved

        #  C1 0 1 3 4 6 7 9        3 approved 3 reproved 1 uncomplete  1 withoutlessons
        #  C2 2  5  8              2 approved 0 reproved 0 uncomplete  1 withoutlessons

        self.assertListEqual(dataset[0]['data'], [2, 3, 1, 1])
        self.assertListEqual(dataset[1]['data'], [2, 0, 0, 1])


    def test_graph_type(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['type'], 'bar')
