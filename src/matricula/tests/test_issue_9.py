from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now

from matricula.models import Category, Course, Period, Group, Enroll, Student
from membership_core.models import Country


class StudentByOrganizationTestCase(TestCase):
    user_count = 1

    def get_enroll(self, group, stud, org_name):
        user = User.objects.create_user(username='user%d'%self.user_count,
                                 email='jacob%d@upo.com'%self.user_count,
                                 password='password')
        self.user_count += 7
        country, created = Country.objects.get_or_create(name='Costa Rica', flag='cr', code='CRC')

        student = Student.objects.create(
            user =  user,
            organization = org_name,
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
        if stud == 0:
            enroll.enroll_finished = False

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

        enroll0 = self.get_enroll(c1g1,0,'ORG')
        enroll0.go_to_one_class = True
        enroll0.course_status = 'approved'

        enroll1 = self.get_enroll(c1g1,1,'org')
        enroll1.go_to_one_class = True
        enroll1.course_status = 'reproved'

        enroll2 = self.get_enroll(c1g1,2,'Org')
        enroll2.go_to_one_class = True
        enroll2.course_status = 'approved'

        enroll3 = self.get_enroll(c1g1,3,'otraorg')
        enroll3.go_to_one_class = True
        enroll3.course_status = 'reproved'

        enroll4 = self.get_enroll(c1g1,4,'Organiza')
        enroll4.go_to_one_class = True
        enroll4.course_status = 'reproved'

        enroll5 = self.get_enroll(c1g1,5,'{"value":"Onda Verde"}')
        enroll5.go_to_one_class = True
        enroll5.course_status = 'approved'

        enroll0.save()
        enroll1.save()
        enroll2.save()
        enroll3.save()
        enroll4.save()
        enroll5.save()

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='juanito2',
                                        email='juanitoCastro@gmail.com',
                                        password='password')
        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()
        self.user.user_permissions.add(view_reports)
        self.url = reverse('student_by_org_report-list')
        self.generate_scenarius()


    def test_graph_data(self):
        '''
           This test verifies if the labels match with the ammount of students enrrolled in the course
        '''
        response = self.client.get(self.url)

        data = response.json()['data']
        dataset = data['datasets']
        dataset_dict = {}
        for item in dataset:
            dataset_dict[item['label']] = item['data']


        self.assertEqual(dataset_dict['org'], [2])  # organiza y Organi
        self.assertEqual(dataset_dict['otraorg'], [1])  # organiza y Organi
        self.assertEqual(dataset_dict['organiza'], [1])  # organiza y Organi
        self.assertEqual(dataset_dict['onda verde'], [1])  # organiza y Organi



    def test_graph_type(self):
        '''
            This test verifies that the graph type is the correct one (bar type)
        '''
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['type'], 'bar')
