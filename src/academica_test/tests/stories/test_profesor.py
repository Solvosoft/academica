"""Historias del profesor."""
import html

from matricula.models import Enroll, Group

from .. import scenario as sc
from .. import xpaths as xp
from ..base import StorySeleniumTestCase


class ProfesorStories(StorySeleniumTestCase):

    def setUp(self):
        super().setUp()
        sc.setup_roles()

    def test_p1_primer_ingreso_completa_su_perfil(self):
        """
        P1. Un profesor nuevo ve el aviso de completar su perfil, lo completa
        (correo para estudiantes y descripción) y el aviso desaparece. La ruta
        antigua de perfil lo lleva al mismo formulario.
        """
        professor = sc.make_professor(complete_profile=False)
        self.login_as(professor)

        self.open('courses')
        self.run_story([
            {"path": xp.text('Es necesario llenar información sobre el rol profesor'), "presence_only": True,
             "caption": "Ve el aviso de completar su perfil"},
            {"path": "//a[contains(@class,'btn-success')][normalize-space(.)='Ir']", "wait_ready": True,
             "caption": "Va a su perfil"},
            {"path": "//input[@name='email_professor']", "extra_action": "setvalue",
             "value": "clases@example.com", "caption": "Indica el correo para estudiantes"},
            {"path": "//textarea[@name='description']", "extra_action": "tinymce",
             "value": "<p>Docente de Python con 10 años de experiencia.</p>", "caption": "Escribe su descripción"},
            {"path": "//form[contains(@action,'profile')]//button[@type='submit']", "wait_ready": True},
            {"path": xp.message('actualizado'), "presence_only": True},
        ], 'p1_perfil')
        profile = self.refresh(professor.professor)
        self.assertEqual(profile.email, 'clases@example.com')
        self.assertIn('10 años', html.unescape(profile.description))

        self.open('courses')
        self.assert_page_not_contains('Es necesario llenar información sobre el rol profesor')
        self.open('edit_profile')
        self.run_story([
            {"path": "//input[@name='email_professor']", "presence_only": True,
             "caption": "La ruta antigua abre el mismo perfil"},
        ], 'p1_ruta_antigua')

    def test_p2_califica_en_lote_y_por_fila(self):
        """
        P2. El profesor solo ve sus grupos. Califica en lote (marca y aplica un
        estado desde el modal) y luego por fila en un grupo de más de 10
        estudiantes: se guardan también las filas de la segunda página.
        """
        professor = sc.make_professor()
        other = sc.make_professor()
        mine = sc.make_group(window='enroll', cost=0, professors=[professor], name='Grupo propio')
        sc.make_group(window='enroll', cost=0, professors=[other], name='Grupo ajeno')
        students = [sc.make_student(first_name='Est%02d' % i) for i in range(12)]
        enrolls = [sc.enroll(s, mine) for s in students]
        self.login_as(professor)

        self.open('groups_enroll')
        self.run_story([
            {"path": xp.text('Grupo propio'), "presence_only": True, "caption": "Solo ve sus grupos"},
        ], 'p2_mis_grupos')
        self.assert_page_not_contains('Grupo ajeno')

        self.open('qualify_students', mine.pk)
        first, second = enrolls[0], enrolls[1]
        self.run_story([
            {"path": "//input[contains(@class,'checkstudent')][@data-id='%d']" % first.pk, "extra_action": "check",
             "caption": "Marca a dos estudiantes"},
            {"path": "//input[contains(@class,'checkstudent')][@data-id='%d']" % second.pk, "extra_action": "check"},
            {"path": "//div[@id='formgroupquality']//a[@data-bs-target='#qualifystudentmodal']",
             "caption": "Abre la calificación en lote"},
            {"path": xp.modal_open('qualifystudentmodal'), "presence_only": True},
            {"path": "//div[@id='qualifystudentmodal']//select[@id='id_course_status']", "extra_action": "select",
             "value": "approved", "caption": "Los aprueba"},
            {"path": "//div[@id='qualifystudentmodal']//button[contains(@onclick,'qualify_status')]",
             "wait_ready": True},
            {"path": "//table[@id='studentstable']", "presence_only": True},
        ], 'p2_lote')
        self.assertEqual(self.refresh(first).course_status, 'approved')
        self.assertEqual(self.refresh(second).course_status, 'approved')

        last = enrolls[-1]  # queda en la segunda página de la tabla (10 por página)
        self.open('qualify_students', mine.pk)
        self.run_story([
            {"path": xp.datatable_page(2), "caption": "Va a la segunda página"},
            {"path": "//select[@id='id_course_status%d']" % last.pk, "extra_action": "select",
             "value": "reproved", "caption": "Reprueba a un estudiante de la segunda página"},
            {"path": xp.datatable_page(1), "caption": "Vuelve a la primera página"},
            {"path": "//select[@id='id_course_status%d']" % first.pk, "extra_action": "select",
             "value": "never_attend"},
            {"path": "//button[contains(@onclick,'json_table')]", "caption": "Guarda la tabla"},
            {"path": xp.swal_title('Calificaciones'), "presence_only": True},
        ], 'p2_por_fila')
        self.assertEqual(self.refresh(last).course_status, 'reproved')
        self.assertEqual(self.refresh(first).course_status, 'never_attend')
        self.assertFalse(first.go_to_one_class)
        self.assertEqual(Enroll.objects.filter(group=mine).count(), 12)
        self.assertEqual(Group.objects.filter(professors=professor.professor).count(), 1)
