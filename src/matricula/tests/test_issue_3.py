from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from matricula.models import Professor, Student

class ListReportsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/reports/'
        view_reports = Permission.objects.filter(codename="view_reports", content_type__app_label="matricula").first()
        professor_group = Group.objects.create(name=settings.PROFESSOR_GROUP_NAME)
        professor_group.permissions.add(view_reports)

        self.student = User.objects.create_user(username='jacob1',
                                        email='jacob1@…',
                                        password='password'),

        self.professor = User.objects.create_user(username='jacob',
                                        email='jacob@…',
                                        password='password')

        self.professor.groups.add(professor_group)


    def test_professor_can_view_report(self):
        '''
        Checks if professor can access to reports list view
        '''
        self.client.login(username='jacob', password='password')
        response = self.client.patch(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_cant_view_report(self):
        '''
        Checks if student can't access to reports list view and get redirect to login instead
        '''
        self.client.login(username='jacob1', password='password')
        response = self.client.patch(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
