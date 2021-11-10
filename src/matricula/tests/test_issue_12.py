from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now
from matricula.models import Category, Course, Period, Group, Enroll, Student
from membership_core.models import Country


class RankingCourseApprovedTestCase(TestCase):
    user_count = 1

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='juanito2',
                                             email='juanitoCastro@gmail.com',
                                             password='password')
        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()
        self.user.user_permissions.add(view_reports)
        self.url = reverse('ranking_course_approved_api-list')
        self.generate_scenarios()

    def get_enroll(self, group):
        user = User.objects.create_user(username='user%d' % self.user_count,
                                        email='jacob%d@upo.com' % self.user_count,
                                        password='password')
        self.user_count += 1

        country, created = Country.objects.get_or_create(name='Costa Rica', flag='cr', code='CRC')
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

    def generate_scenarios(self):
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

        c2g2 = Group.objects.create(
            period=period,
            course=c2,
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

        Country.objects.get_or_create(name='Costa Rica', flag='cr', code='CRC')

        groups = [c1g1, c2g1, c3g1, c2g2]
        for group in groups:
            enroll = self.get_enroll(group)
            enroll.go_to_one_class = True
            if group == groups[2]:
                enroll.course_status = 'reproved'
            else:
                enroll.course_status = 'approved'
            enroll.save()

    def test_draw_data_table(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['draw'], 1)

    def test_dataTable_order(self):
        response = self.client.get(self.url)

        data = response.json()['data']

        self.assertEqual(data[0]['approved_count'], 2)
        self.assertEqual(data[1]['approved_count'], 1)
        self.assertEqual(data[2]['approved_count'], 0)

    def test_total_records(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['recordsTotal'], 3)

    def test_filtered_records(self):
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['recordsFiltered'], 3)
