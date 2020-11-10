# encoding: utf-8

from django.test import TestCase, RequestFactory
from matricula.models import Period, Category, Course, Student, Group

from datetime import  timedelta
from django.utils import timezone as datetime

class InsertTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.period_present = Period.objects.create(
                    name="Test present",
                    start_date=datetime.now(),
                    finish_date=datetime.now() + timedelta(days=1),
                    )

        self.period_past = Period.objects.create(
                    name="Test past",
                    start_date=datetime.now() + timedelta(days=-360),
                    finish_date=datetime.now() + timedelta(days=-2),
                    )
        self.period_future = Period.objects.create(
                    name="Test future",
                    start_date=datetime.now() + timedelta(days=1),
                    finish_date=datetime.now() + timedelta(days=2),
                    )
        self.categorias = [
                Category.objects.create(name="Cat 1", description="Description 1"),
                Category.objects.create(name="Cat 2", description="Description 2"),
                Category.objects.create(name="Cat 3", description="Description 3") 
                          ]

        self.courses = [
            Course.objects.create(category=self.categorias[0],
                                   name="Course 1",
                                   content=""),
            Course.objects.create(category=self.categorias[1],
                                   name="Course 2",
                                   content=""),
            Course.objects.create(category=self.categorias[0],
                                   name="Course 3",
                                   content=""),
            Course.objects.create(category=self.categorias[2],
                                   name="Course 4",
                                   content=""),
                        ]
        self.groups = [
            Group.objects.create(
                        period=self.period_present,
                        course=self.courses[0],
                        name="G 01",
                        schedule="N/D",
                        pre_enroll_start=datetime.now(),
                        pre_enroll_finish=datetime.now() + timedelta(days=1),
                        enroll_start=datetime.now(),
                        enroll_finish=datetime.now() + timedelta(days=1),
                        cost=10.0, maximum=10),
            Group.objects.create(
                        period=self.period_past,
                        course=self.courses[0],
                        name="G 02",
                        schedule="N/D",
                        pre_enroll_start=datetime.now(),
                        pre_enroll_finish=datetime.now() + timedelta(days=1),
                        enroll_start=datetime.now(),
                        enroll_finish=datetime.now() + timedelta(days=1),
                        cost=10.0, maximum=10),
            Group.objects.create(
                        period=self.period_present,
                        course=self.courses[1],
                        name="G 03",
                        schedule="N/D",
                        pre_enroll_start=datetime.now() + timedelta(days=-2),
                        pre_enroll_finish=datetime.now() + timedelta(days=-1),
                        enroll_start=datetime.now(),
                        enroll_finish=datetime.now() + timedelta(days=1),
                        cost=10.0, maximum=10),

                       ]

        self.users = [
                      Student.objects.create_user(username='jacob',
                                                  email='jacob@…',
                                                  password='password'),
                      Student.objects.create_user(username='jacob1',
                                                  email='jacob1@…',
                                                  password='password'),
                      Student.objects.create_user(username='jacob2',
                                                  email='jacob2@…',
                                                  password='password'),
                      Student.objects.create_user(username='jacob3',
                                                  email='jacob3@…',
                                                  password='password'),
                      ]


    def test_demo(self):
        self.assertEqual(True, False)

    def test_demo2(self):
        self.assertEqual(True, True)
