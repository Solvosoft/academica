from matricula.tests.utils import login_report_admin
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.utils.timezone import now
from django.contrib.auth.models import User, Permission
from membership_core.models import Country
from matricula.models import Category, Course, Period, Group, Enroll, Student

class OrganizationsperCountryReportTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        login_report_admin(self.client)
        self.user = User.objects.create_user(username='diego1',
                                        email='diego1@…',
                                        password='12345')
        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()
        self.user.user_permissions.add(view_reports)
        self.url = reverse('organitations_per_country-list')
        self.create_test_case()


    organizations_enroll=1
    def get_organizations_per_country(self, group, user, student):
        user = User.objects.create_user(username='luisdiego%d'%self.organizations_enroll,
                                 email='diego%d@upo.com'%self.organizations_enroll,
                                 password='12345')
        self.organizations_enroll+=1
        country, created =Country.objects.get_or_create(code='CRC', defaults={'name': 'Costa Rica'})
        student = Student.objects.create(
            user =  user,
            organization = 'est',
            country = country,
            city = 'CR',
            phone_number = '86868787',
            expired_at = now()
        )
        enroll = Enroll.objects.create(
            enroll_finished = True,
            enroll_activate = True,
            group = group,
            student = student)
        return enroll

    def create_test_case(self):
        '''
        Test scenario for issue_13
        '''
        ing = Category.objects.create(name='ing1', description='ing1')
        eif004=Course.objects.create(category=ing, name='mat1', content='mat1')
        eif408=Course.objects.create(category=ing, name='ingS2', content='ingS2')
        period = Period.objects.create(name='semestre1', start_date=now(), finish_date=now())

        groupOne = Group.objects.create(
                period = period,
                course = eif004,
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
        groupTwo = Group.objects.create(
                period = period,
                course = eif408,
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
        groupThree = Group.objects.create(
                period = period,
                course = eif408,
                name = 'g3',
                schedule = 'Nothing',
                pre_enroll_start = now(),
                pre_enroll_finish = now(),
                enroll_start = now(),
                enroll_finish = now(),
                cost = 0,
                maximum = 100,
                is_open = True,
                flow = 0)
        groups=[groupOne, groupTwo, groupThree]

        country, created =Country.objects.get_or_create(code='MX', defaults={'name': 'México'})
        student = Student.objects.create(
            user = self.user,
            organization = 'est',
            country = country,
            city = 'MX',
            phone_number = '86868787',
            expired_at = now()
        )

        # México: una organización ("est"), con matrícula activa
        Enroll.objects.create(enroll_finished=True, enroll_activate=True, group=groups[0], student=student)

        # Costa Rica: tres estudiantes de tres organizaciones distintas
        for group, organization in zip(groups, ('org1', 'est1', 'aso1')):
            enroll = self.get_organizations_per_country(group, self.user, student)
            enroll.student.organization = organization
            enroll.student.save()

    def test_organizations_per_country_graph_data(self):
        '''
        Gráfico de pastel: una porción por país con la cantidad de organizaciones distintas.
        '''
        response = self.client.get(self.url)
        data = response.json()['data']
        self.assertEqual(data['labels'], ['Costa Rica', 'México'])
        self.assertListEqual(data['datasets'][0]['data'], [3, 1])

    def test_organizations_per_country_graph_type(self):
        '''
        El reporte se muestra como gráfico de pastel.
        '''
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data['type'], 'pie')
