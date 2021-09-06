from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.models import User, Permission
from membership_core.models import Country
from matricula.models import Category, Course, Period, Group, Enroll, Student

class EnrollsReportTestCase(TestCase):
    student_enroll=1
    def get_enrolls_completed(self, group):
        user = User.objects.create_user(username='luisdiego%d'%self.student_enroll,
                                 email='diego%d@upo.com'%self.student_enroll,
                                 password='12345')
        self.student_enroll+=1
        country, created =Country.objects.get_or_create(name='Costa Rica', flag='cr', code='CRC')
        student = Student.objects.create(
            user =  user,
            organization = 'org',
            country = country,
            city = 'CR',
            phone_number = '63105707',
            expired_at = now()
        )
        enroll = Enroll.objects.create(
            enroll_finished = True,
            enroll_activate = True,
            group = group,
            student = student)
        return enroll

    def create_test_case(self):
        ing = Category.objects.create(name='ing1', description='ing1')
        eif004=Course.objects.create(category=ing, name='mat1', content='mat1')
        eif408=Course.objects.create(category=ing, name='ingS2', content='ingS2')
        #mat001=Enroll.objects.create(enroll_finished=True,  student='mat001')
        period = Period.objects.create(name='semestre1', start_date=now(), finish_date=now())

        ingenieria = Group.objects.create(
                period = period,
                course = eif004,
                name = 'groupOne',
                schedule = 'Nothing',
                pre_enroll_start = now(),
                pre_enroll_finish = now(),
                enroll_start = now(),
                enroll_finish = now(),
                cost = 0,
                maximum = 200,
                is_open = True,
                flow = 0)
        matematicas = Group.objects.create(
                period = period,
                course = eif408,
                name = 'groupTwo',
                schedule = 'Nothing',
                pre_enroll_start = now(),
                pre_enroll_finish = now(),
                enroll_start = now(),
                enroll_finish = now(),
                cost = 0,
                maximum = 200,
                is_open = True,
                flow = 0)
        groups=[ingenieria, matematicas]
        for enroll_student in range(30):
            enroll = self.get_enrolls_completed(groups[enroll_student%2])
            if enroll_student%5 == 0:
            #Se prueban escenarios verificando si el estudiante tiene finalizada la matricula
                enroll.enroll_finished = False
            if enroll_student == 3:
                enroll.enroll_finished = True
            enroll.save()
        '''
        In the template graph there are 2 types of possible scenarios; when there are students enrolled, 
        when there are not students enrolled.
        '''
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='diego1',
                                        email='diego1@…',
                                        password='12345')
        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()
        self.user.user_permissions.add(view_reports)
        self.url = reverse('totalestmatriculados-list')
        self.create_test_case()

    def test_enrolls_student_graph_data(self):
        '''
        Test case for testing graph data
        '''
        enroll_view = self.client.get(self.url)

        data = enroll_view.json()['data']
        dataset = data['datasets']

        #Graph Test data

        #  3 enrolled student
        #  5 non-enrolled student

        #  3 == (eif004,  enrolledstudents = True) 
        #  5 == (eif408,  enrolledstudents = False)
        
        #self.assertListEqual(dataset[0]['data'], [3, 5])
        #self.assertListEqual(dataset[1]['data'], [2, 4])
        self.assertListEqual(dataset[3]['data'], 
        dataset[5]['data'])

    def test_enrolls_student_graph_type(self):
        '''
        Test case to the graph type
        '''
        enroll_view = self.client.get(self.url)
        data = enroll_view.json()
        self.assertEqual(data['type'], 'bar')