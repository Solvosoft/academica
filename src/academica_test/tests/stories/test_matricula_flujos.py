"""Historias que cruzan roles: estudiante y administración durante la matrícula."""
import tempfile
from decimal import Decimal

from matricula.contrib.bills.models import BankBill, Bill
from matricula.models import Coupon, Enroll, Group, WaitingList

from .. import scenario as sc
from .. import xpaths as xp
from ..base import StorySeleniumTestCase

GROUP_MESSAGE = "//div[@id='group_message']//div[contains(., %s)]"


def group_message(text):
    return GROUP_MESSAGE % xp._q(text)


class MatriculaFlujosStories(StorySeleniumTestCase):

    def setUp(self):
        super().setUp()
        sc.setup_roles()
        self.admin = sc.make_academy_admin()

    def pre_enroll_action(self, group, students, action, caption):
        """El administrador marca estudiantes en la lista de pre-inscritos y ejecuta una acción."""
        self.login_as(self.admin)
        self.open('pre_enroll_group', group.pk)
        steps = [{"path": "//input[@name='students'][@data-id='%s']" % s.pk, "extra_action": "check",
                  "caption": "Marca a %s" % s.get_full_name()} for s in students]
        steps.append({"path": "//input[@type='submit'][@value='%s']" % action, "wait_ready": True,
                      "caption": caption})
        return steps

    def test_f1_flujo_normal_preinscripcion_apertura_y_matricula(self):
        """
        F1. Flujo NORMAL: el estudiante se preinscribe, administración abre la
        matrícula para él y, ya en la ventana de matrícula, el estudiante la
        finaliza desde "Mis cursos"; se genera la factura.
        """
        student = sc.make_student()
        group = sc.make_group(window='pre', flow=Group.NORMAL, cost=5000)

        self.login_as(student)
        self.open('course', group.course.pk)
        self.run_story([
            {"path": xp.link('Pre-inscribirme'), "caption": "Se preinscribe"},
            {"path": group_message('Pre-inscripción satisfactoria'), "presence_only": True},
        ], 'f1_preinscripcion')
        enroll = Enroll.objects.get(student=student.student, group=group)
        self.assertFalse(enroll.enroll_activate)
        self.assert_email_sent('email_preenroll_success', student.email)

        self.run_story(self.pre_enroll_action(group, [student], 'Aperturar matrícula',
                                              "Administración abre la matrícula") + [
            {"path": xp.message('activades'), "presence_only": True},
        ], 'f1_apertura')
        self.assertTrue(self.refresh(enroll).enroll_activate)
        self.assert_email_sent('email_open_group', student.email)

        sc.move_group_to(group, 'enroll')
        self.login_as(student)
        self.open('enrollment')
        self.run_story([
            {"path": "//a[contains(@href,'/finish_enroll/%d')]" % enroll.pk, "wait_ready": True,
             "caption": "Finaliza su matrícula desde Mis cursos"},
            {"path": xp.text('Pendientes de pago'), "presence_only": True},
        ], 'f1_finaliza')
        self.assertTrue(self.refresh(enroll).enroll_finished)
        self.assertEqual(Bill.objects.get(enrollment=enroll).amount, Decimal('5000'))

    def test_f2_autopreinscripcion_habilita_la_matricula(self):
        """
        F2. AUTO_PREENROLL: la preinscripción queda activada sola y, al abrirse
        la ventana de matrícula, el estudiante ve "Matricularme" sin intervención.
        """
        student = sc.make_student()
        group = sc.make_group(window='pre', flow=Group.AUTO_PREENROLL, cost=0)
        self.login_as(student)
        self.open('course', group.course.pk)
        self.run_story([
            {"path": xp.link('Pre-inscribirme'), "caption": "Se preinscribe"},
            {"path": group_message('Pre-inscripción satisfactoria'), "presence_only": True},
        ], 'f2_preinscripcion')
        enroll = Enroll.objects.get(student=student.student, group=group)
        self.assertTrue(enroll.enroll_activate, "AUTO_PREENROLL activa la preinscripción")

        sc.move_group_to(group, 'enroll')
        self.open('course', group.course.pk)
        self.run_story([
            {"path": xp.link('Matricularme'), "caption": "Ya puede matricularse"},
            {"path": group_message('Matriculade satisfactoriamente'), "presence_only": True},
        ], 'f2_matricula')
        self.assertTrue(self.refresh(enroll).enroll_finished)

    def test_f3_cupo_lleno_lista_de_espera_y_matricula_desde_espera(self):
        """
        F3. Un grupo con cupo 1 ya está lleno: el estudiante se anota en la lista
        de espera (una sola vez) y administración lo matricula desde ella.
        """
        group = sc.make_group(window='enroll', flow=Group.AUTO_ENROLL, cost=0, maximum=1)
        sc.enroll(sc.make_student(), group)
        student = sc.make_student()

        self.login_as(student)
        self.open('course', group.course.pk)
        self.run_story([
            {"path": xp.link('Matricularme'), "caption": "Intenta matricularse"},
            {"path": group_message('lista de espera'), "presence_only": True, "caption": "El cupo está lleno"},
            {"path": "//div[@id='group_message']//a[contains(.,'Agregarme')]",
             "caption": "Se agrega a la lista de espera"},
            {"path": group_message('realizado exitosamente'), "presence_only": True},
        ], 'f3_lista_espera')
        self.assertTrue(WaitingList.objects.filter(group=group, student=student.student).exists())
        self.assertFalse(Enroll.objects.filter(group=group, student=student.student).exists())

        self.open('course', group.course.pk)
        self.run_story([
            {"path": xp.link('Matricularme')},
            {"path": group_message('ya formas parte de la lista de espera'), "presence_only": True,
             "caption": "Un segundo intento no lo duplica"},
        ], 'f3_repetido')
        self.assertEqual(WaitingList.objects.filter(group=group, student=student.student).count(), 1)

        self.login_as(self.admin)
        self.open('waitinglist_group', group.pk)
        self.run_story([
            {"path": "//button[contains(@class,'enroll')][@id='%s']" % student.pk,
             "caption": "Administración lo matricula desde la lista"},
            {"path": xp.modal_open('exampleModal'), "presence_only": True},
            {"path": "//div[@id='exampleModal']//input[@type='submit']", "wait_ready": True},
        ], 'f3_matricula_desde_espera')
        self.assertTrue(Enroll.objects.filter(group=group, student=student.student,
                                              enroll_finished=True).exists())
        self.assertFalse(WaitingList.objects.filter(group=group, student=student.student).exists())

    def test_f4_cupones_50_100_y_desde_preinscritos(self):
        """
        F4. Cupones: un 50 % deja la factura a la mitad; un 100 % la deja pagada
        con monto 0; no se puede pasar del 100 %. Desde la lista de pre-inscritos
        se asignan cupones solo a los estudiantes marcados.
        """
        group = sc.make_group(window='enroll', flow=Group.AUTO_ENROLL, cost=10000)
        half, full = sc.make_student(), sc.make_student()

        self.login_as(self.admin)
        for student, percentage in ((half, '50'), (full, '100')):
            self.open('create_cupon')
            self.run_story([
                {"path": "//select[@name='student']", "extra_action": "select2",
                 "value": student.get_full_name(), "caption": "Elige al estudiante"},
                {"path": "//select[@name='group']", "extra_action": "select", "value": group.pk},
                {"path": "//select[@name='discount_percentage']", "extra_action": "select", "value": percentage,
                 "caption": "Cupón del %s %%" % percentage},
                {"path": "//form//button[@type='submit']", "wait_ready": True},
                {"path": xp.message('cupón ha sido registrado'), "presence_only": True},
            ], 'f4_cupon_%s' % percentage)
            self.assert_email_sent('coupon_code_notification', student.email)

        self.open('create_cupon')
        self.run_story([
            {"path": "//select[@name='student']", "extra_action": "select2", "value": full.get_full_name()},
            {"path": "//select[@name='group']", "extra_action": "select", "value": group.pk},
            {"path": "//select[@name='discount_percentage']", "extra_action": "select", "value": '50'},
            {"path": "//form//button[@type='submit']", "wait_ready": True,
             "caption": "Intenta pasar del 100 %"},
            {"path": xp.message('ya tiene el 100%'), "presence_only": True},
        ], 'f4_cupon_excedido')
        self.assertEqual(Coupon.objects.filter(student=full.student).count(), 1)

        for student in (half, full):
            self.login_as(student)
            self.open('course', group.course.pk)
            self.run_story([
                {"path": xp.link('Matricularme'), "caption": "Se matricula con cupón"},
                {"path": group_message('Matriculade satisfactoriamente'), "presence_only": True},
            ], 'f4_matricula_con_cupon')
        half_bill = Bill.objects.get(student=half.student)
        full_bill = Bill.objects.get(student=full.student)
        self.assertEqual(half_bill.amount, Decimal('5000'))
        self.assertFalse(half_bill.is_paid)
        self.assertEqual(full_bill.amount, Decimal('0'))
        self.assertTrue(full_bill.is_paid, "Una beca completa no deja la factura pendiente")

        pre_group = sc.make_group(window='pre', flow=Group.NORMAL, cost=8000)
        marked, unmarked = sc.make_student(), sc.make_student()
        for student in (marked, unmarked):
            sc.enroll(student, pre_group, enroll_activate=False, enroll_finished=False)
        self.login_as(self.admin)
        self.open('pre_enroll_group', pre_group.pk)
        self.run_story([
            {"path": "//input[@name='students'][@data-id='%s']" % marked.pk, "extra_action": "check",
             "caption": "Marca solo a un estudiante"},
            {"path": "//a[@id='assigncouponsbutton']", "caption": "Asigna cupones"},
            {"path": xp.modal_open('assigncouponsmodal'), "presence_only": True},
            {"path": "//select[@id='id_discount_percentage']", "extra_action": "select", "value": '50'},
            {"path": "//div[@id='assigncouponsmodal']//*[contains(@onclick,'assign_coupons')]"},
            {"path": xp.swal_title('Cupones'), "presence_only": True},
            {"path": "//*[contains(@class,'swal2-success')]", "presence_only": True,
             "caption": "Se confirma la asignación"},
        ], 'f4_cupones_preinscritos')
        self.assertTrue(Coupon.objects.filter(student=marked.student, group=pre_group,
                                              discount_percentage=50).exists())
        self.assertFalse(Coupon.objects.filter(student=unmarked.student, group=pre_group).exists())

    def test_f5_rechazo_de_preinscripcion(self):
        """F5. Administración rechaza una preinscripción; el estudiante la ve rechazada."""
        student = sc.make_student()
        group = sc.make_group(window='pre', flow=Group.NORMAL)
        enroll = sc.enroll(student, group, enroll_activate=False, enroll_finished=False)

        self.run_story(self.pre_enroll_action(group, [student], 'Rechazar pre-inscripción',
                                              "Administración rechaza la preinscripción") + [
            {"path": xp.message('notificades'), "presence_only": True},
        ], 'f5_rechazo')
        self.assertTrue(self.refresh(enroll).rejected)
        self.assert_email_sent('email_enroll_rejected', student.email)

        self.login_as(student)
        self.open('enrollment')
        self.run_story([
            {"path": "//a[contains(@class,'disabled')][contains(normalize-space(.),'Rechazada')]",
             "presence_only": True, "caption": "El estudiante ve su preinscripción rechazada"},
        ], 'f5_estudiante')

    def test_f6_pago_por_deposito_verificado_por_administracion(self):
        """
        F6. El estudiante reporta un depósito con su comprobante; el superusuario
        lo aprueba en el admin y la factura pasa a "Pagos Realizados".
        """
        student = sc.make_student()
        group = sc.make_group(window='enroll', flow=Group.AUTO_ENROLL, cost=12000)
        sc.enroll(student, group)
        bill = Bill.objects.get(student=student.student)
        voucher = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        voucher.write(b'%PDF-1.4 comprobante')
        voucher.close()

        self.login_as(student)
        self.open('bills')
        bank_form = "//form[contains(@action,'banktransfer')]"
        self.run_story([
            {"path": bank_form + "//input[@name='payment_document']", "extra_action": "upload",
             "value": voucher.name, "caption": "Adjunta el comprobante del depósito"},
            {"path": bank_form + "//textarea[@name='description']", "extra_action": "setvalue",
             "value": "Cédula 2-2222-2222"},
            {"path": bank_form + "//button[@type='submit']", "wait_ready": True, "caption": "Reporta el pago"},
            {"path": xp.message('Recibimos su reporte de pago'), "presence_only": True},
        ], 'f6_deposito')
        deposit = BankBill.objects.get(bill=bill)
        self.assert_mail_outbox('New Bank payment')

        self.login_as(sc.make_superuser())
        self.open('/admin/bills/bankbill/')
        self.run_story([
            {"path": "//input[@name='_selected_action'][@value='%s']" % deposit.pk, "extra_action": "check",
             "caption": "El superusuario selecciona el depósito"},
            {"path": "//select[@name='action']", "extra_action": "select", "value": 'approve_payment'},
            {"path": "//button[@name='index']", "wait_ready": True, "caption": "Aprueba el pago"},
        ], 'f6_aprobacion')
        self.assertTrue(self.refresh(bill).is_paid)
        self.assertTrue(self.refresh(deposit).verified)

        self.login_as(student)
        self.open('bills')
        self.run_story([
            {"path": xp.text("No tiene pagos pendientes"), "presence_only": True,
             "caption": "Ya no tiene pagos pendientes"},
        ], 'f6_estudiante')

    def test_f7_editar_y_eliminar_cupon_recalcula_la_factura(self):
        """
        F7. Administración sube un cupón del 50 % al 100 %: la factura queda
        pagada por beca. Luego elimina el cupón: la factura vuelve a estar
        pendiente por el costo completo.
        """
        group = sc.make_group(window='enroll', flow=Group.AUTO_ENROLL, cost=10000)
        student = sc.make_student()
        from matricula import coupons
        coupon = coupons.create_coupon(student.student, group, 50)
        sc.enroll(student, group)
        bill = Bill.objects.get(student=student.student)
        self.assertEqual(bill.amount, Decimal('5000'))

        self.login_as(self.admin)
        self.open('edit_coupon', coupon.pk)
        self.run_story([
            {"path": "//select[@name='discount_percentage']", "extra_action": "select", "value": '100',
             "caption": "Sube el cupón al 100 %"},
            {"path": "//form//button[@type='submit']", "wait_ready": True},
            {"path": xp.message('actualizado'), "presence_only": True},
        ], 'f7_editar')
        bill = self.refresh(bill)
        self.assertEqual((bill.amount, bill.is_paid), (Decimal('0'), True))
        self.assert_email_sent('coupon_code_notification_updated', student.email)

        self.open('coupons_list')
        self.run_story([
            {"path": "//a[contains(@data-url,'/coupons/%d/delete')]" % coupon.pk,
             "caption": "Elimina el cupón"},
            {"path": xp.modal_open('modaldeletecoupon'), "presence_only": True},
            {"path": "//a[@id='deletecoupon']", "wait_ready": True, "caption": "Confirma"},
            {"path": xp.message('Cupón eliminado'), "presence_only": True},
        ], 'f7_eliminar')
        bill = self.refresh(bill)
        self.assertFalse(Coupon.objects.filter(pk=coupon.pk).exists())
        self.assertEqual((bill.amount, bill.is_paid), (Decimal('10000'), False))
