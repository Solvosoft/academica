"""Historias del visitante y del estudiante."""
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User

from matricula.contrib.bills.models import Bill, CardPayment, SinpeMovilBill
from matricula.models import Enroll, Group, Student

from .. import scenario as sc
from .. import xpaths as xp
from ..base import StorySeleniumTestCase
from ..fakes import patch_card_service


class EstudianteStories(StorySeleniumTestCase):

    def setUp(self):
        super().setUp()
        sc.setup_roles()

    def test_e2_matricula_grupo_pagado_y_pago_sinpe(self):
        """
        E2. Un estudiante inicia sesión con su correo, se matricula en un grupo
        pagado y reporta el pago por Sinpe Móvil.

        Reglas: la matrícula finalizada crea la factura por el costo del grupo,
        se encola el correo de matrícula y el pago Sinpe avisa a administración.
        """
        student = sc.make_student(email='ana@example.com')
        group = sc.make_group(window='enroll', flow=Group.AUTO_ENROLL, cost=15000)

        self.open('login')
        steps = self.login_steps('ana@example.com', sc.PASSWORD)
        self.run_story(steps, 'e2_login_correo')

        self.open('course', group.course.pk)
        self.run_story([
            {"path": xp.text(group.name), "presence_only": True, "caption": "Ve el grupo abierto"},
            {"path": xp.link('Matricularme'), "caption": "Se matricula"},
            {"path": "//div[@id='group_message']//div[contains(., 'Matriculade satisfactoriamente')]",
             "presence_only": True},
            {"path": "//div[@id='group_message']//a[contains(., 'Pagar ahora')]", "wait_ready": True,
             "caption": "Va a pagar"},
            {"path": xp.PAGE_BILLS, "presence_only": True},
        ], 'e2_matricula')

        enroll = Enroll.objects.get(student=student.student, group=group)
        self.assertTrue(enroll.enroll_finished)
        bill = Bill.objects.get(enrollment=enroll)
        self.assertEqual(bill.amount, Decimal('15000'))
        self.assertFalse(bill.is_paid)
        self.assert_email_sent('email_enroll_success', 'ana@example.com')
        self.assert_page_contains('15000')

        sinpe_form = "//form[contains(@action,'sinpemovil')]"
        self.run_story([
            {"path": sinpe_form + "//input[@name='transaction_code']", "extra_action": "setvalue",
             "value": "SINPE-123", "caption": "Anota el código del comprobante Sinpe"},
            {"path": sinpe_form + "//textarea[@name='description']", "extra_action": "setvalue",
             "value": "Cédula 1-1111-1111"},
            {"path": sinpe_form + "//button[@type='submit']", "wait_ready": True, "caption": "Reporta el pago"},
            {"path": xp.message('Recibimos su reporte de pago'), "presence_only": True},
            {"path": xp.text('Estamos procesando su pago'), "presence_only": True,
             "caption": "La factura queda en verificación"},
        ], 'e2_pago_sinpe')

        self.assertTrue(SinpeMovilBill.objects.filter(bill=bill, transaction_code='SINPE-123').exists())
        self.assert_mail_outbox('New SinpeMovil payment')
        self.assertTrue(settings.PAYMENT_NOTIFICATION_MAIL)

    def test_e1_registro_de_visitante(self):
        """
        E1. Un visitante ve el catálogo, se registra (primero con una contraseña
        débil, que el sistema rechaza) y queda con la sesión iniciada.

        Reglas: el usuario se llena desde el correo, se crea el Student y se envía
        el correo de bienvenida new_user_created_academy.
        """
        group = sc.make_group(window='pre', flow=Group.NORMAL)

        self.open('course', group.course.pk)
        form = "//form[.//input[@id='id_password']]"
        self.run_story([
            {"path": xp.text(group.name), "presence_only": True, "caption": "El visitante ve el grupo"},
            {"path": "//a[@id='get-started-btn']", "wait_ready": True, "caption": "Hace clic en Registrarme"},
            {"path": form + "//input[@id='id_first_name']", "extra_action": "setvalue", "value": "Luisa"},
            {"path": form + "//input[@id='id_last_name']", "extra_action": "setvalue", "value": "Vargas Mora"},
            {"path": form + "//input[@id='id_email']", "extra_action": "setvalue",
             "value": "luisa.vargas@example.com", "caption": "Escribe su correo"},
            {"path": form + "//input[@id='id_email']", "extra_action": "script",
             "value": "jQuery(arguments[0]).trigger('change');"},
            {"path": form + "//input[@id='id_phone_number']", "extra_action": "setvalue", "value": "88887777"},
            {"path": form + "//input[@id='id_organization']", "extra_action": "script",
             "value": "tagify.addTags(['Universidad de Costa Rica']);", "caption": "Indica su organización"},
            {"path": form + "//input[@id='id_password']", "extra_action": "setvalue", "value": "debil",
             "caption": "Usa una contraseña débil"},
            {"path": form + "//button[@type='submit']", "wait_ready": True},
            {"path": form + "//input[@id='id_password']", "presence_only": True,
             "caption": "El formulario la rechaza"},
        ], 'e1_registro_rechazado')
        self.assertFalse(User.objects.filter(email='luisa.vargas@example.com').exists())
        self.assertEqual(self.find(form + "//input[@id='id_name']").get_attribute('value'), 'luisa.vargas',
                         "El usuario de acceso debe llenarse desde el correo")

        self.run_story([
            {"path": form + "//input[@id='id_organization']", "extra_action": "script",
             "value": "tagify.removeAllTags(); tagify.addTags(['Universidad de Costa Rica']);"},
            {"path": form + "//input[@id='id_password']", "extra_action": "setvalue",
             "value": sc.PASSWORD, "caption": "Corrige la contraseña"},
            {"path": form + "//button[@type='submit']", "wait_ready": True, "caption": "Se registra"},
            {"path": xp.link('Cerrar sesión'), "presence_only": True, "caption": "Queda con sesión iniciada"},
        ], 'e1_registro_exitoso')

        user = User.objects.get(email='luisa.vargas@example.com')
        self.assertEqual(user.username, 'luisa.vargas')
        student = Student.objects.get(user=user)
        self.assertIn('Universidad de Costa Rica', student.organization)
        self.assert_email_sent('new_user_created_academy', 'luisa.vargas@example.com')

    def test_e3_matricula_en_grupo_gratuito(self):
        """
        E3. Matrícula en un grupo gratuito: no se genera factura y el curso
        aparece como matriculado en "Mis cursos" y en el historial.
        """
        student = sc.make_student()
        group = sc.make_group(window='enroll', flow=Group.AUTO_ENROLL, cost=0)
        self.login_as(student)

        self.open('course', group.course.pk)
        self.run_story([
            {"path": xp.text('Curso gratis'), "presence_only": True},
            {"path": xp.link('Matricularme'), "caption": "Se matricula en el grupo gratuito"},
            {"path": "//div[@id='group_message']//div[contains(., 'Matriculade satisfactoriamente')]",
             "presence_only": True},
        ], 'e3_matricula_gratis')
        enroll = Enroll.objects.get(student=student.student, group=group)
        self.assertTrue(enroll.enroll_finished)
        self.assertFalse(Bill.objects.filter(enrollment=enroll).exists(), "Un grupo gratuito no genera factura")

        self.open('enrollment')
        self.run_story([
            {"path": xp.text('Cursos Matriculados'), "presence_only": True},
            {"path": xp.link(group.name), "presence_only": True, "caption": "Lo ve en Mis cursos"},
        ], 'e3_mis_cursos')
        self.open('student_history')
        self.run_story([
            {"path": xp.text(group.name), "presence_only": True, "caption": "Y en su historial"},
        ], 'e3_historial')

    def test_e4_pago_con_tarjeta(self):
        """
        E4. El estudiante paga su factura con tarjeta: va al checkout del
        servicio de pagos (simulado), vuelve aprobado y la factura queda pagada.
        """
        service = patch_card_service(self)
        student = sc.make_student()
        group = sc.make_group(window='enroll', flow=Group.AUTO_ENROLL, cost=20000)
        sc.enroll(student, group)
        bill = Bill.objects.get(enrollment__group=group)
        self.login_as(student)

        self.open('bills')
        card_form = "//form[contains(@action,'/pay/card/')]"
        self.run_story([
            {"path": xp.text('Tarjeta de crédito o débito'), "presence_only": True},
            {"path": xp.text('20000,00 CRC'), "presence_only": True, "caption": "Ve el monto a cobrar"},
            {"path": card_form + "//button", "wait_ready": True, "caption": "Paga con tarjeta"},
            {"path": xp.message('pago con tarjeta fue aprobado'), "presence_only": True,
             "caption": "Vuelve con el pago aprobado"},
            {"path": xp.text('Pagos Realizados'), "presence_only": True},
        ], 'e4_pago_tarjeta')

        self.assertTrue(self.refresh(bill).is_paid)
        payment = CardPayment.objects.get(bill=bill)
        self.assertEqual(payment.status, CardPayment.Status.COMPLETED)
        self.assertEqual(service.count('post', '/api/v1/orders/'), 1)
        self.assert_email_sent('email_invoice_academy', student.email)
        self.assert_page_not_contains('Pagar con tarjeta')

    def test_e5_perfil_y_recuperacion_de_contrasena(self):
        """
        E5. El estudiante actualiza su perfil; luego olvida la contraseña, el
        administrador le envía la recuperación y la cambia con el enlace del correo
        (que solo sirve una vez). Al final inicia sesión con la contraseña nueva.
        """
        student = sc.make_student()
        admin = sc.make_academy_admin()
        self.login_as(student)

        self.open('myprofile', student.pk)
        self.run_story([
            {"path": "//input[@name='phone_number']", "extra_action": "setvalue", "value": "70001234",
             "caption": "Actualiza su teléfono"},
            {"path": "//input[@name='city']", "extra_action": "setvalue", "value": "Cartago"},
            {"path": "//form[contains(@action,'profile')]//button[@type='submit']", "wait_ready": True,
             "caption": "Guarda el perfil"},
            {"path": xp.message('actualizado'), "presence_only": True},
        ], 'e5_perfil')
        self.assertEqual(self.refresh(student.student).phone_number, '70001234')
        self.assertEqual(student.student.city, 'Cartago')

        self.logout()
        self.login_as(admin)
        self.open('students')
        self.run_story([
            {"path": "//a[contains(@href, '/recovery_pass_student/%d/')]" % student.pk, "wait_ready": True,
             "caption": "El administrador le envía la recuperación"},
            {"path": xp.message('correo de recuperación'), "presence_only": True},
        ], 'e5_admin_recupera')
        self.assert_email_sent('email_recovery_academy', student.email)
        key = self.refresh(student.student).key

        self.logout()
        self.open('recover_password', query='key=%s' % key)
        self.run_story([
            {"path": "//input[@id='id_password']", "extra_action": "setvalue", "value": 'Nueva#Clave2026',
             "caption": "Abre el enlace del correo y escribe una contraseña nueva"},
            {"path": "//form//button[@type='submit']", "wait_ready": True},
            {"path": xp.message('cambiada con éxito'), "presence_only": True},
        ], 'e5_nueva_clave')
        self.assertNotEqual(self.refresh(student.student).key, key, "El enlace debe dejar de servir")
        self.open('recover_password', query='key=%s' % key)
        self.assertIn('Not Found', self.selenium.title + self.find('//body').text)

        self.open('login')
        self.run_story(self.login_steps(student.username, 'Nueva#Clave2026') + [
            {"path": xp.link('Cerrar sesión'), "presence_only": True, "caption": "Entra con la contraseña nueva"},
        ], 'e5_login_nueva_clave')
