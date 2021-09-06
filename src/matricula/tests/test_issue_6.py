from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now

from matricula.models import Category, Course, Period, Group, Enroll, Student
from membership_core.models import SystemCurrency, Country


class Uncompleted_Student_TestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='mariovaargas',
                                        email='mariovargasc97@gmail.com',
                                        password='password')
        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()
        self.user.user_permissions.add(view_reports)
        self.url = reverse('uncompleted_student-list')
        self.generate_scenarius()


    def get_enroll(self, group, user, student):
        enroll = Enroll.objects.create(
            enroll_finished=True,
            enroll_activate=True,
            group=group,
            student=student,
            course_status="approved")
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

        c3g2 = Group.objects.create(
            period=period,
            course=c3,
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

        groups = [c1g1, c2g1, c3g1, c3g2]

        country, created = Country.objects.get_or_create(name='Costa Rica', flag='cr', code='CRC')
        student = Student.objects.create(
            user=self.user,
            organization='org',
            country=country,
            city='CR',
            phone_number='88888888',
            expired_at=now()
        )

        enroll1 = self.get_enroll(groups[0], self.user, student)
        enroll1.go_to_one_class = True
        enroll1.course_status = "approved"

        enroll2 = self.get_enroll(groups[1], self.user, student)
        enroll2.go_to_one_class = True
        enroll2.course_status = "uncomplete"

        enroll3 = self.get_enroll(groups[2], self.user, student)
        enroll3.go_to_one_class = False
        enroll3.course_status = "uncomplete"

        enroll4 = self.get_enroll(groups[3], self.user, student)
        enroll4.go_to_one_class = True
        enroll4.course_status = "uncomplete"

        enroll1.save()
        enroll2.save()
        enroll3.save()
        enroll4.save()


    def test_graph_data(self):
        response = self.client.get(self.url)

        data = response.json()['data']
        dataset = data['datasets']

        self.assertEqual(dataset[0]['data'], [0])
        self.assertEqual(dataset[1]['data'], [1])
        self.assertEqual(dataset[2]['data'], [1])


    def test_graph_type(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['type'], 'bar')
