from datetime import datetime

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now

from matricula.models import Category, Course, Period, Group, Enroll, Student
from membership_core.models import SystemCurrency, Country


class Courses_By_Year_TestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(username='nombre1',
                                         email='prueba1@gmail.com',
                                         password='password1')

        self.user2 = User.objects.create_user(username='nombre2',
                                         email='prueba2@gmail.com',
                                         password='password2')

        self.user3 = User.objects.create_user(username='nombre3',
                                         email='prueba3@gmail.com',
                                         password='password3')

        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()
        self.user1.user_permissions.add(view_reports)
        self.user2.user_permissions.add(view_reports)
        self.user3.user_permissions.add(view_reports)
        self.url = reverse('total_courses_by_year-list')
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
        period1 = Period.objects.create(name='per1', start_date=now(), finish_date=now())
        period2 = Period.objects.create(name='per2', start_date='2026-10-10', finish_date='2027-10-10')
        period3 = Period.objects.create(name='per3', start_date='2010-11-11', finish_date='2011-11-11')

        c1g1 = Group.objects.create(
            period=period1,
            course=c1,
            name='g1',
            schedule='Nothing',
            pre_enroll_start=now(),
            pre_enroll_finish=now(),
            enroll_start=datetime(2004, 1, 1),
            enroll_finish=datetime(2009, 11, 11),
            cost=0,
            maximum=200,
            is_open=True,
            flow=0)

        c2g1 = Group.objects.create(
            period=period1,
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
            period=period2,
            course=c3,
            name='g1',
            schedule='Nothing',
            pre_enroll_start=now(),
            pre_enroll_finish=now(),
            enroll_start=datetime(2008, 1, 1),
            enroll_finish=datetime(2011, 1, 1),
            cost=0,
            maximum=200,
            is_open=True,
            flow=0)

        c3g2 = Group.objects.create(
            period=period3,
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

        country1 = Country.objects.create(name='Costa Rica', flag='cr', code='CR')
        country2 = Country.objects.create(name='Afganistán', flag='af', code='AF')
        country3 = Country.objects.create(name='Australia', flag='au', code='AU')

        student1 = Student.objects.create(
            user=self.user1,
            organization='org',
            country=country1,
            city='CR',
            phone_number='88888888',
            expired_at=now()
        )

        student2 = Student.objects.create(
            user=self.user2,
            organization='org',
            country=country2,
            city='AF',
            phone_number='88888888',
            expired_at=now()
        )

        student3 = Student.objects.create(
            user=self.user3,
            organization='org',
            country=country3,
            city='AU',
            phone_number='88888888',
            expired_at=now()
        )

        enroll1 = self.get_enroll(groups[0], self.user1, student1)
        enroll1.go_to_one_class = False
        enroll1.course_status = "uncomplete"

        enroll2 = self.get_enroll(groups[1], self.user1, student1)
        enroll2.go_to_one_class = True
        enroll2.course_status = "reproved"

        enroll3 = self.get_enroll(groups[2], self.user3, student3)
        enroll3.go_to_one_class = False
        enroll3.course_status = "approved"

        enroll4 = self.get_enroll(groups[3], self.user2, student2)
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

        self.assertEqual(dataset[0]['data'], [1])
        self.assertEqual(dataset[1]['data'], [1])
        self.assertEqual(dataset[2]['data'], [2])


    def test_graph_type(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['type'], 'bar')


    def test_graph_title(self):
        response = self.client.get(self.url)

        options = response.json()['options']
        data = options['title']
        self.assertEqual(data['text'], 'Reporte total de cursos por año')


    def test_graph_labels(self):
        response = self.client.get(self.url)

        data = response.json()['data']
        self.assertEqual(data['labels'], ['Año correspondiente al curso'])


class Courses_By_Month_TestCase(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(username='nombre1',
                                         email='prueba1@gmail.com',
                                         password='password1')

        self.user2 = User.objects.create_user(username='nombre2',
                                         email='prueba2@gmail.com',
                                         password='password2')

        self.user3 = User.objects.create_user(username='nombre3',
                                         email='prueba3@gmail.com',
                                         password='password3')

        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()
        self.user1.user_permissions.add(view_reports)
        self.user2.user_permissions.add(view_reports)
        self.user3.user_permissions.add(view_reports)
        self.url = reverse('total_courses_by_month-list')
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
        period1 = Period.objects.create(name='per1', start_date=now(), finish_date=now())
        period2 = Period.objects.create(name='per2', start_date='2026-10-10', finish_date='2027-10-10')
        period3 = Period.objects.create(name='per3', start_date='2010-11-11', finish_date='2011-11-11')

        c1g1 = Group.objects.create(
            period=period1,
            course=c1,
            name='g1',
            schedule='Nothing',
            pre_enroll_start=now(),
            pre_enroll_finish=now(),
            enroll_start=datetime(2004, 1, 1),
            enroll_finish=datetime(2005, 1, 1),
            cost=0,
            maximum=200,
            is_open=True,
            flow=0)

        c2g1 = Group.objects.create(
            period=period1,
            course=c2,
            name='g1',
            schedule='Nothing',
            pre_enroll_start=now(),
            pre_enroll_finish=now(),
            enroll_start=datetime(2007, 1, 1),
            enroll_finish=datetime(2009, 2, 1),
            cost=0,
            maximum=200,
            is_open=True,
            flow=0)

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

        c3g2 = Group.objects.create(
            period=period3,
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

        country1 = Country.objects.create(name='Costa Rica', flag='cr', code='CR')
        country2 = Country.objects.create(name='Afganistán', flag='af', code='AF')
        country3 = Country.objects.create(name='Australia', flag='au', code='AU')

        student1 = Student.objects.create(
            user=self.user1,
            organization='org',
            country=country1,
            city='CR',
            phone_number='88888888',
            expired_at=now()
        )

        student2 = Student.objects.create(
            user=self.user2,
            organization='org',
            country=country2,
            city='AF',
            phone_number='88888888',
            expired_at=now()
        )

        student3 = Student.objects.create(
            user=self.user3,
            organization='org',
            country=country3,
            city='AU',
            phone_number='88888888',
            expired_at=now()
        )

        enroll1 = self.get_enroll(groups[0], self.user1, student1)
        enroll1.go_to_one_class = False
        enroll1.course_status = "uncomplete"

        enroll2 = self.get_enroll(groups[1], self.user1, student1)
        enroll2.go_to_one_class = True
        enroll2.course_status = "reproved"

        enroll3 = self.get_enroll(groups[2], self.user3, student3)
        enroll3.go_to_one_class = False
        enroll3.course_status = "approved"

        enroll4 = self.get_enroll(groups[3], self.user2, student2)
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

        self.assertEqual(dataset[0]['data'], [1])
        self.assertEqual(dataset[1]['data'], [1])
        self.assertEqual(dataset[2]['data'], [2])


    def test_graph_type(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['type'], 'bar')


    def test_graph_title(self):
        response = self.client.get(self.url)

        options = response.json()['options']
        data = options['title']
        self.assertEqual(data['text'], 'Reporte total de cursos por mes')


    def test_graph_labels(self):
        response = self.client.get(self.url)

        data = response.json()['data']
        self.assertEqual(data['labels'], ['Mes correspondiente al curso'])