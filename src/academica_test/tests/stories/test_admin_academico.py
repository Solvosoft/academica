"""Historias del administrador académico."""
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from djgentelella.models import MenuItem as DJMenuItem
from matricula.models import Category, Course, Enroll, Group, Page, Period, Student
from membership_core.models import Country, SystemCurrency

from .. import scenario as sc
from .. import xpaths as xp
from ..base import StorySeleniumTestCase


def fmt_date(value):
    return value.strftime('%d/%m/%Y')


def fmt_datetime(value):
    return timezone.localtime(value).strftime('%d/%m/%Y %H:%M')


class AdminAcademicoStories(StorySeleniumTestCase):

    def setUp(self):
        super().setUp()
        sc.setup_roles()
        self.admin = sc.make_academy_admin()

    def test_a1_armar_la_oferta_periodo_categoria_curso_y_grupo(self):
        """
        A1. Administración crea periodo, categoría, curso y grupo desde las
        pantallas; los errores de fechas se rechazan y, al final, un visitante ve
        el grupo en el catálogo.
        """
        professor = sc.make_professor()
        today = timezone.localdate()
        self.login_as(self.admin)

        self.open('periods')
        period_form = "//form[contains(@action,'create_period')]"
        self.run_story([
            {"path": period_form + "//input[@name='name']", "extra_action": "setvalue", "value": "2026-II",
             "caption": "Crea el periodo con fechas invertidas"},
            {"path": period_form + "//input[@name='start_date']", "extra_action": "jsvalue",
             "value": fmt_date(today + timezone.timedelta(days=30))},
            {"path": period_form + "//input[@name='finish_date']", "extra_action": "jsvalue",
             "value": fmt_date(today - timezone.timedelta(days=30))},
            {"path": period_form + "//input[@type='submit']", "wait_ready": True},
            {"path": xp.message('Error al guardar el periodo'), "presence_only": True,
             "caption": "El sistema rechaza el rango"},
        ], 'a1_periodo_invalido')
        self.assertFalse(Period.objects.filter(name='2026-II').exists())

        self.open('periods')
        self.run_story([
            {"path": period_form + "//input[@name='name']", "extra_action": "setvalue", "value": "2026-II"},
            {"path": period_form + "//input[@name='start_date']", "extra_action": "jsvalue",
             "value": fmt_date(today - timezone.timedelta(days=30))},
            {"path": period_form + "//input[@name='finish_date']", "extra_action": "jsvalue",
             "value": fmt_date(today + timezone.timedelta(days=90)), "caption": "Corrige las fechas"},
            {"path": period_form + "//input[@type='submit']", "wait_ready": True},
            {"path": xp.message('Periodo guardado'), "presence_only": True},
        ], 'a1_periodo')
        period = Period.objects.get(name='2026-II')

        self.open('categories')
        category_form = "//form[contains(@action,'create_category')]"
        self.run_story([
            {"path": category_form + "//input[@name='name']", "extra_action": "setvalue",
             "value": "Ciencia de datos", "caption": "Crea la categoría"},
            {"path": category_form + "//*[@name='description']", "extra_action": "setvalue",
             "value": "Análisis y visualización"},
            {"path": category_form + "//input[@type='submit']", "wait_ready": True},
            {"path": xp.message('Registro creado'), "presence_only": True},
        ], 'a1_categoria')
        self.assertTrue(Category.objects.filter(name='Ciencia de datos').exists())

        self.open('create_course')
        self.run_story([
            {"path": "//select[@name='category']", "extra_action": "select2", "value": "Ciencia",
             "caption": "Elige la categoría"},
            {"path": "//input[@name='name']", "extra_action": "setvalue", "value": "Pandas desde cero"},
            {"path": "//textarea[@name='content']", "extra_action": "tinymce",
             "value": "<p>Temario: series, dataframes y gráficos.</p>", "caption": "Escribe el temario"},
            {"path": "//input[@type='submit'][@value='Guardar']", "wait_ready": True},
            {"path": xp.message('Curso guardado'), "presence_only": True},
        ], 'a1_curso')
        course = Course.objects.get(name='Pandas desde cero')
        self.assertIn('dataframes', course.content)

        now = timezone.now()
        day = timezone.timedelta(days=1)
        group_steps = [
            {"path": "//input[@name='name']", "extra_action": "setvalue", "value": "Pandas G1",
             "caption": "Crea el grupo"},
            {"path": "//select[@name='course']", "extra_action": "select", "value": course.pk},
            {"path": "//select[@name='period']", "extra_action": "select2", "value": "2026-II"},
            {"path": "//input[@name='schedule']", "extra_action": "setvalue", "value": "Martes 6pm"},
            {"path": "//input[@name='pre_enroll_start']", "extra_action": "jsvalue",
             "value": fmt_datetime(now - day)},
            {"path": "//input[@name='pre_enroll_finish']", "extra_action": "jsvalue",
             "value": fmt_datetime(now + 5 * day), "caption": "La prematrícula termina después..."},
            {"path": "//input[@name='enroll_start']", "extra_action": "jsvalue",
             "value": fmt_datetime(now + 2 * day), "caption": "...de que empieza la matrícula"},
            {"path": "//input[@name='enroll_finish']", "extra_action": "jsvalue",
             "value": fmt_datetime(now + 10 * day)},
            {"path": "//input[@name='is_paid']", "extra_action": "check"},
            {"path": "//select[@name='currency']", "extra_action": "select",
             "value": SystemCurrency.objects.get(currency='CRC').pk},
            {"path": "//input[@name='cost']", "extra_action": "setvalue", "value": "25000"},
            {"path": "//input[@name='maximum']", "extra_action": "setvalue", "value": "15"},
            {"path": "//select[@name='flow']", "extra_action": "select", "value": Group.NORMAL},
            {"path": "//select[@name='professors']", "extra_action": "select",
             "value": professor.professor.pk},
            {"path": "//input[@type='submit'][@value='Guardar']", "wait_ready": True},
        ]
        self.open('create_group_enroll')
        self.run_story(group_steps + [
            {"path": xp.text('Error en rangos de fechas'), "presence_only": True,
             "caption": "El sistema rechaza los rangos traslapados"},
        ], 'a1_grupo_invalido')
        self.assertFalse(Group.objects.filter(name='Pandas G1').exists())

        group_steps[6]['value'] = fmt_datetime(now + 6 * day)
        self.open('create_group_enroll')
        self.run_story(group_steps + [
            {"path": xp.message('Grupo guardado'), "presence_only": True},
        ], 'a1_grupo')
        group = Group.objects.get(name='Pandas G1')
        self.assertEqual((group.cost, group.period, group.flow), (Decimal('25000'), period, Group.NORMAL))
        self.assertTrue(group.in_preenrollment)
        self.assertIn(professor.professor, group.professors.all())

        self.logout()
        self.open('course', course.pk)
        self.run_story([
            {"path": xp.text('Pandas G1'), "presence_only": True, "caption": "Un visitante ve el grupo"},
            {"path": xp.text('25000'), "presence_only": True},
            {"path": xp.text(professor.get_full_name()), "presence_only": True},
            {"path": xp.link('Pre-inscribirme'), "presence_only": True,
             "caption": "Y se le invita a preinscribirse"},
        ], 'a1_catalogo_publico')

    def test_a2_cerrar_y_abrir_grupo_con_notificacion(self):
        """
        A2. Administración cierra un grupo notificando a los estudiantes: las
        matrículas quedan inactivas y el grupo sale del catálogo; al abrirlo de
        nuevo y notificar, el botón queda como "Ya se notificó".
        """
        group = sc.make_group(window='enroll', flow=Group.AUTO_ENROLL, cost=0)
        student = sc.make_student()
        enroll = sc.enroll(student, group)
        self.login_as(self.admin)

        self.open('list_students_group', group.pk)
        self.run_story([
            {"path": xp.link('Cerrar grupo y'), "wait_ready": True, "caption": "Cierra el grupo y notifica"},
        ], 'a2_cerrar')
        self.assertFalse(self.refresh(group).is_open)
        self.assertFalse(self.refresh(enroll).enroll_activate)
        self.assert_email_sent('email_close_group', student.email)

        self.logout()
        self.open('course', group.course.pk)
        self.assert_page_not_contains(group.name)

        self.login_as(self.admin)
        self.open('list_students_group', group.pk)
        self.run_story([
            {"path": xp.link('Abrir grupo y'), "wait_ready": True, "caption": "Lo abre y notifica"},
        ], 'a2_abrir')
        self.open('list_students_group', group.pk)
        self.run_story([
            {"path": xp.link('Ya se notifico de apertura'), "presence_only": True,
             "caption": "No se puede notificar dos veces"},
        ], 'a2_ya_notificado')
        self.assertTrue(self.refresh(group).is_open)
        self.assert_email_sent('email_open_group', student.email)

    def test_a3_gestion_de_estudiantes(self):
        """
        A3. Administración busca estudiantes, crea uno sin contraseña (se le
        envía el correo para definirla), exporta los correos y elimina un
        registro de prueba con el modal de confirmación.
        """
        existing = sc.make_student(first_name='Marta', last_name='Solano')
        disposable = sc.make_student(first_name='Temporal', last_name='Borrar')
        self.login_as(self.admin)

        self.open('students')
        self.run_story([
            {"path": "//select[@name='student']", "extra_action": "select2", "value": "Marta Solano",
             "caption": "Busca a una estudiante"},
            {"path": "//input[@type='submit'][@value='Buscar']", "wait_ready": True},
            {"path": xp.text('Marta Solano'), "presence_only": True},
        ], 'a3_busqueda')
        self.assert_page_not_contains('Temporal Borrar')

        self.open('create_student')
        new_form = "//form[.//input[@name='new']]"
        self.run_story([
            {"path": new_form + "//input[@name='username']", "extra_action": "setvalue", "value": "pedro.rojas",
             "caption": "Crea un estudiante nuevo"},
            {"path": new_form + "//input[@name='first_name']", "extra_action": "setvalue", "value": "Pedro"},
            {"path": new_form + "//input[@name='last_name']", "extra_action": "setvalue", "value": "Rojas"},
            {"path": new_form + "//input[@name='email']", "extra_action": "setvalue",
             "value": "pedro.rojas@example.com"},
            {"path": new_form + "//input[@name='organization']", "extra_action": "setvalue", "value": "TEC"},
            {"path": new_form + "//input[@name='city']", "extra_action": "setvalue", "value": "Heredia"},
            {"path": new_form + "//input[@name='phone_number']", "extra_action": "setvalue", "value": "60001111"},
            {"path": new_form + "//select[@name='country']", "extra_action": "select",
             "value": Country.objects.get(code='CR').pk},
            {"path": new_form + "//input[@name='new']", "wait_ready": True},
            {"path": xp.message('guardade con éxito'), "presence_only": True},
        ], 'a3_crear')
        pedro = User.objects.get(username='pedro.rojas')
        self.assertTrue(Student.objects.filter(user=pedro).exists())
        self.assertFalse(pedro.has_usable_password() and pedro.check_password(''))
        self.assert_email_sent('set_email_first_academy', 'pedro.rojas@example.com')

        # La descarga no se ve en el navegador: se pide con la misma sesión.
        self.client.cookies[settings.SESSION_COOKIE_NAME] = self.selenium.get_cookie(
            settings.SESSION_COOKIE_NAME)['value']
        response = self.client.get(reverse('students'), {'action': 'Exportar correos'})
        self.assertEqual(response['Content-Type'],
                         'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Un GET a la URL de borrado ya no borra (solo POST con CSRF desde el modal)
        response = self.client.get(reverse('delete_student', args=[disposable.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Student.objects.filter(user=disposable).exists())

        self.open('students')
        self.run_story([
            {"path": "//a[contains(@data-url,'/delete_student/%d/')]" % disposable.pk,
             "caption": "Pide eliminar el registro de prueba"},
            {"path": xp.modal_open('modaldeleteitem'), "presence_only": True,
             "caption": "Se abre la confirmación"},
            {"path": xp.DELETE_MODAL_CONFIRM, "wait_ready": True, "caption": "Confirma"},
        ], 'a3_eliminar')
        self.assertFalse(Student.objects.filter(user=disposable).exists())
        self.assertTrue(Student.objects.filter(user=existing).exists())

    def test_a4_catalogos_y_tipo_de_cambio(self):
        """
        A4. Administración crea, edita y elimina un país y una moneda en los
        catálogos. El tipo de cambio de una moneda cambia el monto que se cobra
        con tarjeta a una factura en esa moneda (convertido a USD).
        """
        self.login_as(self.admin)
        self.open('catalog_country')
        self.run_story([
            {"path": xp.gt_crud_table_ready('country_table'), "presence_only": True},
            {"path": "//button[contains(@class,'btn') and .//i[contains(@class,'fa-plus')]]",
             "caption": "Agrega un país"},
            {"path": xp.modal_open('create_obj_modal'), "presence_only": True},
            {"path": "//input[@id='id_create-name']", "extra_action": "setvalue", "value": "Atlántida"},
            {"path": "//input[@id='id_create-code']", "extra_action": "setvalue", "value": "ZZ"},
            {"path": xp.modal_save('create_obj_modal'), "caption": "Lo guarda"},
            {"path": xp.modal_closed('create_obj_modal'), "presence_only": True},
            {"path": "//input[@type='search']", "extra_action": "setvalue", "value": "Atlántida",
             "caption": "Lo busca en la tabla"},
            {"path": "//table[@id='country_table']//td[contains(.,'Atlántida')]", "presence_only": True},
        ], 'a4_pais')
        self.assertTrue(Country.objects.filter(code='ZZ', name='Atlántida').exists())

        eur = SystemCurrency.objects.create(currency='EUR', rates=Decimal('0.50'))
        group = sc.make_group(window='enroll', cost=100, currency_code='EUR')
        student = sc.make_student()
        sc.enroll(student, group)
        self.login_as(student)
        self.open('bills')
        self.assert_page_contains('200,00 USD')

        self.login_as(self.admin)
        self.open('catalog_currency')
        self.run_story([
            {"path": xp.gt_crud_row_action('currency_table', 'EUR', 'fa-edit'),
             "caption": "Edita el tipo de cambio del euro"},
            {"path": xp.modal_open('update_obj_modal'), "presence_only": True},
            {"path": "//input[@id='id_update-rates']", "extra_action": "setvalue", "value": "0.80"},
            {"path": xp.modal_save('update_obj_modal')},
            {"path": xp.modal_closed('update_obj_modal'), "presence_only": True},
            {"path": "//table[@id='currency_table']//td[contains(.,'0.80') or contains(.,'0,80')]",
             "presence_only": True, "caption": "La tabla muestra el nuevo tipo de cambio"},
        ], 'a4_moneda')
        self.assertEqual(self.refresh(eur).rates, Decimal('0.80'))

        self.login_as(student)
        self.open('bills')
        self.assert_page_contains('125,00 USD')

    def test_a5_pagina_con_menu(self):
        """A5. Administración crea una página con entrada de menú; el visitante la abre desde el menú."""
        self.login_as(self.admin)
        self.open('create_page')
        self.run_story([
            {"path": "//input[@name='title']", "extra_action": "setvalue", "value": "Preguntas frecuentes",
             "caption": "Crea la página"},
            {"path": "//input[@name='slug']", "extra_action": "setvalue", "value": "faq"},
            {"path": "//textarea[@name='content']", "extra_action": "tinymce",
             "value": "<p>¿Cómo me matriculo? Desde el catálogo.</p>"},
            {"path": "//input[@name='create_menu']", "extra_action": "check",
             "caption": "La agrega al menú"},
            {"path": "//input[@type='submit'][@value='Guardar']", "wait_ready": True},
            {"path": xp.message('Página guardada'), "presence_only": True},
        ], 'a5_pagina')
        self.assertTrue(Page.objects.filter(slug='faq').exists())
        self.assertTrue(DJMenuItem.objects.filter(url_name__contains='faq').exists())

        self.logout()
        self.open('root')
        self.run_story([
            {"path": xp.link('Preguntas frecuentes'), "wait_ready": True,
             "caption": "El visitante la abre desde el menú"},
            {"path": xp.text('¿Cómo me matriculo?'), "presence_only": True},
        ], 'a5_visitante')

    def test_a6_recorrido_de_reportes(self):
        """A6. Administración recorre todos los reportes: cada uno carga sin errores."""
        group = sc.make_group(window='enroll', cost=0)
        for status in ('approved', 'reproved'):
            sc.enroll(sc.make_student(), group, course_status=status)
        self.login_as(self.admin)
        self.open('list_reports')
        report_links = [a.get_attribute('href') for a in self.selenium.find_elements(
            'xpath', "//a[contains(@class,'list-group-item')]")]
        self.assertGreaterEqual(len(report_links), 10)
        for href in report_links:
            self.selenium.get(href)
            self.wait_for_ready()
            self.assert_no_server_error()
            self.assertNotIn('403', self.selenium.title)
        self.assertFalse(Enroll.objects.filter(group=group).exclude(course_status__in=['approved', 'reproved']))
