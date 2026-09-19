"""Historias de permisos por rol y del superusuario."""
import shutil
import unittest

from django.contrib.auth.models import User

from matricula.models import Enroll, Group, Professor

from .. import scenario as sc
from .. import xpaths as xp
from ..base import StorySeleniumTestCase

SIDEBAR = "//div[contains(@class,'left_col')]"


def sidebar_section(name):
    return SIDEBAR + "//a[contains(normalize-space(.), %s)]" % xp._q(name)


class PermisosStories(StorySeleniumTestCase):

    def setUp(self):
        super().setUp()
        sc.setup_roles()

    def sidebar_text(self):
        return self.find(SIDEBAR).text

    def test_r1_estudiante_no_entra_a_la_administracion(self):
        """R1. Un estudiante solo ve "Matrícula" y las pantallas de administración lo rechazan."""
        self.login_as(sc.make_student())
        self.open('courses')
        sidebar = self.sidebar_text()
        self.assertIn('Matrícula', sidebar)
        for section in ('Académica', 'Catálogos', 'Administración'):
            self.assertNotIn(section, sidebar)
        self.assertEqual(self.selenium.find_elements('xpath', SIDEBAR + "//a[contains(@href,'/bills/list')]"), [])
        for urlname in ('groups_enroll', 'students', 'list_reports', 'listbills', 'catalog_country'):
            self.open(urlname)
            self.assertIn('/accounts/login/', self.selenium.current_url,
                          "%s debería pedir otro usuario" % urlname)

    def test_r2_profesor_ve_solo_lo_suyo(self):
        """R2. El profesor ve Grupos y Reportes, pero no Estudiantes ni Pagos, ni grupos ajenos."""
        professor = sc.make_professor()
        foreign = sc.make_group(window='enroll', professors=[sc.make_professor()])
        self.login_as(professor)
        self.open('courses')
        self.run_story([
            {"path": sidebar_section('Académica'), "caption": "Abre la sección Académica"},
            {"path": SIDEBAR + "//a[contains(@href,'/enrrolment/groups')]", "presence_only": True},
            {"path": SIDEBAR + "//a[contains(@href,'/reports/')]", "presence_only": True},
        ], 'r2_sidebar')
        for admin_link in ('/enrrolment/students', '/bills/list', '/catalog/'):
            self.assertEqual(self.selenium.find_elements(
                'xpath', SIDEBAR + "//a[contains(@href,'%s')]" % admin_link), [],
                "El profesor no debería ver %s" % admin_link)
        self.open('list_students_group', foreign.pk)
        self.assertIn('/accounts/login/', self.selenium.current_url)
        self.open('qualify_students', foreign.pk)
        self.assertNotIn('/qualify_students', self.selenium.current_url)

    def test_r3_administrador_academico(self):
        """R3. Administración académica ve Académica, Catálogos y Pagos, pero no la gestión de usuarios."""
        self.login_as(sc.make_academy_admin())
        self.open('home')
        sidebar = self.sidebar_text()
        for section in ('Académica', 'Catálogos'):
            self.assertIn(section, sidebar)
        self.find(SIDEBAR + "//a[contains(@href,'/bills/list')]")
        self.assertNotIn('Administración', sidebar)
        self.open('user_list')
        self.assertIn('/accounts/login/', self.selenium.current_url)

    def test_s1_superusuario_crea_profesor_y_genera_certificados(self):
        """
        S1. El superusuario crea un usuario con el grupo Profesores (se crea su
        perfil de profesor y se le avisa por correo) y genera los certificados
        de un grupo con estudiantes aprobados.
        """
        root = sc.make_superuser()
        self.login_as(root)
        self.open('create_user')
        self.run_story([
            {"path": "//input[@name='username']", "extra_action": "setvalue", "value": "profe.nuevo",
             "caption": "Crea un usuario"},
            {"path": "//input[@name='first_name']", "extra_action": "setvalue", "value": "Carla"},
            {"path": "//input[@name='last_name']", "extra_action": "setvalue", "value": "Méndez"},
            {"path": "//input[@name='email']", "extra_action": "setvalue", "value": "carla@example.com"},
            {"path": "//select[@name='fakegroups']", "extra_action": "select2", "value": "Profesores",
             "caption": "Le asigna el grupo Profesores"},
            {"path": "//form//button[@type='submit'] | //form//input[@type='submit']", "wait_ready": True},
        ], 's1_usuario')
        carla = User.objects.get(username='profe.nuevo')
        self.assertTrue(Professor.objects.filter(user=carla).exists())
        self.assert_email_sent('new_user_created_membership', 'carla@example.com')

        if not shutil.which('rsvg-convert'):
            raise unittest.SkipTest("rsvg-convert no está instalado: se omite la generación de certificados")
        group = sc.make_group(window='enroll', cost=0)
        approved = sc.enroll(sc.make_student(), group, course_status='approved')
        reproved = sc.enroll(sc.make_student(), group, course_status='reproved')
        self.open('list_students_group', group.pk)
        self.run_story([
            {"path": xp.link('Generar'), "wait_ready": True, "caption": "Genera los certificados"},
            {"path": xp.message('Certificados'), "presence_only": True},
        ], 's1_certificados')
        self.assertTrue(self.refresh(approved).pdf_certificate)
        self.assertFalse(self.refresh(reproved).pdf_certificate)
        self.assertEqual(Enroll.objects.filter(group=group).count(), 2)
        self.assertEqual(Group.objects.count(), 1)
