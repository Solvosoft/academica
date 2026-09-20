"""
`/media/certificates/` y `/media/bank/` son privados.

Antes los servia nginx directo desde el disco: con la URL bastaba, sin sesion,
para bajar el certificado de cualquier estudiante o el comprobante de deposito
de cualquier pago (nombre del depositante, monto y la imagen del comprobante).
"""
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.utils.timezone import now

from matricula.contrib.bills.models import Bill, BankBill
from matricula.models import Category, Course, Enroll, Group, Period, Student
from membership_core.models import Country, SystemCurrency


class MediaAccessTest(TestCase):
    def setUp(self):
        self.dueno = User.objects.create_user(username='dueno', email='d@x.com',
                                              password='pass-dueno')
        self.otro = User.objects.create_user(username='otro', email='o@x.com',
                                             password='pass-otro')
        self.profesor = User.objects.create_user(username='profe', email='p@x.com',
                                                 password='pass-profe')
        self.profesor.user_permissions.add(
            Permission.objects.get(codename='view_enroll',
                                   content_type__app_label='matricula'))

        pais = Country.objects.get_or_create(code='CR', defaults={'name': 'Costa Rica'})[0]
        self.estudiante = Student.objects.create(
            user=self.dueno, organization='org', country=pais, city='CR',
            phone_number='88888888', expired_at=now())
        Student.objects.create(
            user=self.otro, organization='org', country=pais, city='CR',
            phone_number='88888888', expired_at=now())

        categoria = Category.objects.create(name='cat', description='cat')
        curso = Course.objects.create(category=categoria, name='curso', content='curso')
        periodo = Period.objects.create(name='per', start_date='2030-01-01',
                                        finish_date='2030-06-30')
        grupo = Group.objects.create(
            period=periodo, course=curso, name='g1', schedule='nada',
            pre_enroll_start=now(), pre_enroll_finish=now(),
            enroll_start=now(), enroll_finish=now(),
            cost=0, maximum=10, is_open=True, flow=0)

        self.enroll = Enroll.objects.create(
            enroll_finished=True, enroll_activate=True, group=grupo,
            student=self.estudiante, course_status='approved',
            pdf_certificate='certificates/certificado-1.pdf')

        moneda = SystemCurrency.objects.first()
        bill = Bill.objects.create(
            short_description='matricula', description='matricula', amount=1000,
            student=self.estudiante,
            **({'currency': moneda} if moneda else {}))
        BankBill.objects.create(
            name='Quien deposita', group_name='grupo', bill=bill,
            description='factura', payment_document='bank/comprobante-1.png')

        self.certificado = '/media/certificates/certificado-1.pdf'
        self.comprobante = '/media/bank/comprobante-1.png'

    def test_anonymous_is_sent_to_the_login(self):
        for url in (self.certificado, self.comprobante):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn('/accounts/login/', response['Location'])

    def test_another_student_cannot_read_them(self):
        self.client.force_login(self.otro)
        for url in (self.certificado, self.comprobante):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_the_owner_reads_them_through_nginx(self):
        self.client.force_login(self.dueno)
        for url in (self.certificado, self.comprobante):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                # El archivo lo entrega nginx, no Django: la respuesta va vacia
                # y solo dice cual.
                self.assertEqual(response['X-Accel-Redirect'],
                                 '/_protected/' + url[len('/media/'):])
                self.assertEqual(response.content, b'')

    def test_staff_reads_them(self):
        # El profesor ve el listado de su grupo, donde esta el enlace.
        self.client.force_login(self.profesor)
        self.assertEqual(self.client.get(self.certificado).status_code, 200)

    def test_a_file_that_is_not_theirs_is_denied_even_if_it_exists(self):
        # El dueno de un certificado no puede pedir el de otro cambiando el
        # nombre en la URL.
        self.client.force_login(self.dueno)
        response = self.client.get('/media/certificates/certificado-de-otro.pdf')
        self.assertEqual(response.status_code, 403)
