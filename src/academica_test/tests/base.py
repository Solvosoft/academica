"""
Base de las pruebas de navegación por historias de usuario.

Cada prueba recorre varias pantallas como lo haría un rol real. Los pasos se
describen como una lista de diccionarios (el mismo DSL de organilab)::

    self.run_story([
        {"path": xp.link("Matricularme"), "caption": "Se matricula"},
        {"path": xp.message("Matriculade"), "presence_only": True},
    ], "e2_matricula")

Claves de un paso:

``path``            XPath del elemento (obligatorio).
``extra_action``    ``setvalue`` | ``jsvalue`` | ``clear`` | ``script`` | ``select`` |
                    ``select2`` | ``tinymce`` | ``upload`` | ``check`` | ``uncheck``.
                    Sin ``extra_action`` el paso hace clic.
``value``           Valor de la acción.
``presence_only``   Solo espera a que el elemento exista.
``wait_ready``      Espera a que la página termine de cargar (después del paso).
``force_click``     Permite clic por JS aunque el elemento esté oculto.
``caption``         Texto que describe el paso (se dibuja en el GIF).

Las corridas se hacen bajo ``xvfb-run`` desde el Makefile para no abrir
ventanas en el escritorio (``make test-selenium``).
"""
import os
import re
import time
from importlib import import_module
from pathlib import Path

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import mail
from django.core.signals import got_request_exception
from django.db import OperationalError, connections
from django.test import tag
from django.urls import reverse
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException, ElementNotInteractableException,
                                        JavascriptException, MoveTargetOutOfBoundsException,
                                        StaleElementReferenceException, TimeoutException,
                                        UnexpectedAlertPresentException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from djgentelella.async_notification.models import EmailNotification

from . import xpaths as xp

ELEMENT_TIMEOUT = int(os.getenv('SELENIUM_ELEMENT_TIMEOUT', '10'))
READY_TIMEOUT = int(os.getenv('SELENIUM_READY_TIMEOUT', '15'))
WINDOW_SIZE = (1280, 720)


def _slug(text):
    return re.sub(r'[^a-zA-Z0-9_-]+', '_', text).strip('_')[:80]


@tag('selenium')
class StorySeleniumTestCase(StaticLiveServerTestCase):
    """Caso base: un navegador Chromium por clase, historias como listas de pasos."""

    host = '127.0.0.1'
    # El live server vacía la BD al terminar cada historia; con esto se restauran
    # los datos que cargan las migraciones (países, monedas, plantillas de correo).
    serialized_rollback = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.unhandled_prompt_behavior = 'dismiss'
        # Sin este capability las navegaciones se colgaban en organilab.
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        for arg in ('--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu',
                    '--window-size=%d,%d' % WINDOW_SIZE, '--lang=es'):
            options.add_argument(arg)
        # El sitio se prueba en español (LocaleMiddleware usa Accept-Language).
        options.add_experimental_option('prefs', {'intl.accept_languages': 'es-CR,es'})
        if os.getenv('SELENIUM_HEADLESS') == '1':
            options.add_argument('--headless=new')
        binary = os.getenv('CHROME_BINARY')
        if binary:
            options.binary_location = binary
        driver_path = os.getenv('CHROMEDRIVER_PATH')
        service = webdriver.ChromeService(executable_path=driver_path) if driver_path else None
        cls.selenium = webdriver.Chrome(options=options, service=service)
        client_config = getattr(cls.selenium.command_executor, '_client_config', None)
        if client_config is not None:
            client_config.timeout = int(os.getenv('SELENIUM_COMMAND_TIMEOUT', '60'))
        cls.selenium.set_page_load_timeout(int(os.getenv('SELENIUM_PAGE_LOAD_TIMEOUT', '45')))
        cls.selenium.set_script_timeout(int(os.getenv('SELENIUM_SCRIPT_TIMEOUT', '30')))
        cls.selenium.set_window_size(*WINDOW_SIZE)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    # --- ciclo de vida ------------------------------------------------------

    def setUp(self):
        super().setUp()
        self.server_errors = []
        got_request_exception.connect(self._on_server_error)
        self.results_dir = Path(settings.SELENIUM_RESULTS_DIR)
        self.selenium.delete_all_cookies()

    def tearDown(self):
        got_request_exception.disconnect(self._on_server_error)
        self.quiesce_browser()
        super().tearDown()
        if self.server_errors:
            self.fail("El servidor lanzó excepciones durante la historia:\n" + "\n".join(self.server_errors))

    def _on_server_error(self, sender, request=None, **kwargs):
        import sys
        import traceback
        exc = sys.exc_info()
        self.server_errors.append("%s %s\n%s" % (
            getattr(request, 'method', ''), getattr(request, 'path', ''),
            ''.join(traceback.format_exception(*exc)) if exc[0] else ''))

    def quiesce_browser(self):
        """Evita que una petición en vuelo choque con el flush de la base de datos."""
        try:
            self.wait_for_idle(timeout=5)
            self.selenium.get('about:blank')
        except Exception:
            pass

    def _fixture_teardown(self):
        try:
            super()._fixture_teardown()
        except OperationalError:
            # Deadlock ocasional entre el TRUNCATE y la última petición del navegador.
            for connection in connections.all():
                connection.close()
            super()._fixture_teardown()

    # --- navegación y sesión ------------------------------------------------

    def url(self, urlname, *args, query=''):
        path = reverse(urlname, args=args) if not urlname.startswith('/') else urlname
        return self.live_server_url + path + (('?' + query) if query else '')

    def open(self, urlname, *args, query=''):
        self.selenium.get(self.url(urlname, *args, query=query))
        try:
            self.wait_for_ready()
        except UnexpectedAlertPresentException as exc:
            # Un alert de JS (p. ej. "DataTables warning") es un error de la página.
            raise AssertionError("La página %s mostró un alert: %s" % (urlname, exc.alert_text))
        self.assert_no_server_error()

    def login_as(self, user):
        """Inicia sesión creando la cookie de sesión (sin pasar por el formulario)."""
        engine = import_module(settings.SESSION_ENGINE)
        self.selenium.get(self.live_server_url + reverse('login'))
        session = engine.SessionStore()
        session[SESSION_KEY] = user._meta.pk.value_to_string(user)
        session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
        session[HASH_SESSION_KEY] = user.get_session_auth_hash()
        session.save()
        self.selenium.delete_all_cookies()
        self.selenium.add_cookie({'name': settings.SESSION_COOKIE_NAME,
                                  'value': session.session_key, 'path': '/'})

    def logout(self):
        self.selenium.get(self.live_server_url + '/')
        self.selenium.delete_all_cookies()

    def login_steps(self, identifier, password):
        """Pasos para iniciar sesión por el formulario (usuario o correo)."""
        return [
            {"path": "//input[@name='username']", "extra_action": "setvalue", "value": identifier,
             "caption": "Escribe su usuario o correo"},
            {"path": "//input[@name='password']", "extra_action": "setvalue", "value": password},
            {"path": "//button[@type='submit']", "wait_ready": True, "caption": "Inicia sesión"},
        ]

    # --- esperas ------------------------------------------------------------

    def wait_for_ready(self, timeout=READY_TIMEOUT):
        try:
            WebDriverWait(self.selenium, timeout).until(
                lambda d: d.execute_script(
                    "return document.readyState === 'complete' && (!document.body"
                    " || document.body.getAttribute('data-test-ready') === 'true');"))
        except TimeoutException:
            pass
        self.wait_for_idle(timeout=timeout)

    def wait_for_idle(self, timeout=READY_TIMEOUT):
        WebDriverWait(self.selenium, timeout).until(lambda d: d.execute_script(
            "return document.readyState === 'complete'"
            " && (!window.jQuery || jQuery.active === 0)"
            " && (window.__testPendingDT === undefined || window.__testPendingDT === 0);"))

    def find(self, xpath, timeout=ELEMENT_TIMEOUT):
        try:
            return WebDriverWait(self.selenium, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            raise AssertionError("No apareció el elemento %s en %s" % (xpath, self.selenium.current_url))

    def assert_no_server_error(self):
        title = self.selenium.title or ''
        body = self.selenium.find_element(By.TAG_NAME, 'body').text[:500] if self.selenium.page_source else ''
        if 'Server Error' in title or 'Server Error (500)' in body:
            raise AssertionError("Error 500 en %s" % self.selenium.current_url)

    # --- ejecución de historias ---------------------------------------------

    def run_story(self, steps, name):
        frames = []
        total = len(steps)
        for index, step in enumerate(steps, start=1):
            error = None
            try:
                if settings.GENERATE_SCREENSHOTS:
                    frames.append(self._frame(step, index, total, before=True))
                self._run_step(step)
                if settings.GENERATE_SCREENSHOTS:
                    frames.append(self._frame(step, index, total, before=False))
            except (AssertionError, TimeoutException, JavascriptException, UnexpectedAlertPresentException,
                    StaleElementReferenceException, ElementNotInteractableException) as exc:
                error = "paso %d/%d de '%s' (%s) | xpath=%s | url=%s | %s" % (
                    index, total, name, step.get('caption', ''), step.get('path'),
                    self.selenium.current_url, str(exc).splitlines()[0] if str(exc) else type(exc).__name__)
            if error:
                self._save_failure(name, index)
                # Fuera del except: sin traceback encadenado (tblib + --parallel)
                raise AssertionError(error)
        if frames:
            self._save_gif(frames, name)

    def _run_step(self, step):
        xpath = step['path']
        action = step.get('extra_action')
        element = self.find(xpath)
        if step.get('presence_only'):
            return
        value = step.get('value')
        if action is None:
            self.click(element, xpath, force=step.get('force_click', False))
        elif action == 'setvalue':
            self._set_value(element, xpath, value, clear=step.get('clear', True))
        elif action == 'clear':
            element.clear()
        elif action == 'jsvalue':
            # Campos con máscara o selector de fecha: se asigna el valor y se avisa el cambio.
            self.selenium.execute_script(
                "var el=arguments[0]; el.value=arguments[1];"
                "el.dispatchEvent(new Event('input',{bubbles:true}));"
                "el.dispatchEvent(new Event('change',{bubbles:true}));"
                "if (window.jQuery) jQuery(el).trigger('change');", element, str(value))
        elif action == 'script':
            self.selenium.execute_script(value, element)
        elif action == 'select':
            self.selenium.execute_script(
                "var el=arguments[0]; el.value=arguments[1];"
                "el.dispatchEvent(new Event('change',{bubbles:true}));"
                "if (window.jQuery) jQuery(el).trigger('change');", element, str(value))
        elif action == 'select2':
            self._select2_search(element, value)
        elif action == 'tinymce':
            self.selenium.execute_script(
                "var id=arguments[0].id, html=arguments[1];"
                "var ed = window.tinymce && tinymce.get(id);"
                "if (ed) { ed.setContent(html); ed.save(); } else { arguments[0].value = html; }",
                element, value)
        elif action == 'upload':
            element.send_keys(str(value))
        elif action in ('check', 'uncheck'):
            wanted = action == 'check'
            if element.is_selected() != wanted:
                self.selenium.execute_script(
                    "arguments[0].checked=arguments[1];"
                    "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));"
                    "if (window.jQuery) jQuery(arguments[0]).trigger('change');", element, wanted)
        else:
            raise AssertionError("extra_action desconocida: %s" % action)
        if step.get('wait_ready'):
            self.wait_for_ready()
            self.assert_no_server_error()
        else:
            self.wait_for_idle()

    def click(self, element, xpath, force=False):
        self.selenium.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        for attempt in range(2):
            try:
                WebDriverWait(self.selenium, 3).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            except TimeoutException:
                pass
            try:
                element.click()
                return
            except (ElementClickInterceptedException, MoveTargetOutOfBoundsException):
                break
            except (StaleElementReferenceException, ElementNotInteractableException):
                if attempt == 0:
                    element = self.find(xpath)
                    continue
                break
        if not element.is_displayed() and not force:
            raise AssertionError("El elemento %s está oculto: un clic por JS sería un falso verde" % xpath)
        self.selenium.execute_script("arguments[0].click();", element)

    def _set_value(self, element, xpath, value, clear=True):
        try:
            if clear:
                element.clear()
            element.send_keys(str(value))
        except (ElementNotInteractableException, StaleElementReferenceException):
            element = self.find(xpath)
            self.selenium.execute_script(
                "arguments[0].value=arguments[1];"
                "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", element, str(value))

    def _select2_search(self, element, text):
        """Abre el select2 del <select> ``element``, escribe ``text`` y elige el resultado que lo contiene."""
        field_id = element.get_attribute('id')
        multiple = element.get_attribute('multiple')
        search_xpath = xp.select2_inline_search(field_id) if multiple else xp.SELECT2_SEARCH
        result_xpath = "(%s[contains(normalize-space(.), %s)])[1]" % (xp.SELECT2_REAL_RESULT, xp._q(text))
        last_error = None
        # select2 vuelve a dibujar el buscador y los resultados mientras se escribe.
        for _attempt in range(3):
            try:
                self.click(self.find(xp.select2_field(field_id)), xp.select2_field(field_id))
                search = self.find(search_xpath)
                search.clear()
                search.send_keys(text)
                # select2 espera (debounce) antes de consultar; luego redibuja la lista.
                time.sleep(0.6)
                self.wait_for_idle()
                self.click(self.find(result_xpath), result_xpath)
                return
            except (StaleElementReferenceException, AssertionError) as exc:
                last_error = exc
                time.sleep(0.5)
        raise AssertionError("select2 %s: no se pudo elegir '%s' (%s)" % (field_id, text, last_error))

    # --- aserciones de negocio ----------------------------------------------

    def assert_page_contains(self, text):
        body = self.find('//body').text
        self.assertIn(text, body, "No se encontró '%s' en %s" % (text, self.selenium.current_url))

    def assert_page_not_contains(self, text):
        self.assertNotIn(text, self.find('//body').text)

    def assert_email_sent(self, code_subject, recipient, enqueued=None):
        """Verifica que djgentelella registró el correo (por asunto) al destinatario."""
        from matricula.utils import EMAIL_TEMPLATES
        subjects = {code: subject for code, subject, *_ in EMAIL_TEMPLATES}
        subject = subjects.get(code_subject, code_subject)
        notifications = EmailNotification.objects.filter(recipients__contains=[recipient])
        matches = [n for n in notifications if n.subject == subject]
        self.assertTrue(matches, "No se envió '%s' a %s. Enviados: %s" % (
            code_subject, recipient, [n.subject for n in notifications]))
        return matches[-1]

    def assert_mail_outbox(self, subject_part):
        self.assertTrue(any(subject_part in m.subject for m in mail.outbox),
                        "No hay correo con '%s' en el outbox: %s" % (
                            subject_part, [m.subject for m in mail.outbox]))

    def refresh(self, obj):
        obj.refresh_from_db()
        return obj

    # --- capturas -----------------------------------------------------------

    def _save_failure(self, name, index):
        folder = self.results_dir / 'fallas'
        folder.mkdir(parents=True, exist_ok=True)
        base = folder / ('%s_%s_paso%d' % (_slug(self.id().split('.')[-1]), _slug(name), index))
        try:
            self.selenium.save_screenshot(str(base) + '.png')
            base.with_suffix('.html').write_text(self.selenium.page_source, encoding='utf-8')
        except Exception:
            pass

    def _frame(self, step, index, total, before):
        from io import BytesIO

        from PIL import Image, ImageDraw, ImageFont
        if not before:
            time.sleep(0.3)
        image = Image.open(BytesIO(self.selenium.get_screenshot_as_png())).convert('RGB')
        caption = step.get('caption')
        if caption:
            draw = ImageDraw.Draw(image)
            text = "%d/%d  %s" % (index, total, caption)
            try:
                font = ImageFont.truetype('DejaVuSans.ttf', 18)
            except OSError:
                font = ImageFont.load_default()
            draw.rectangle([0, image.height - 36, image.width, image.height], fill=(33, 37, 41))
            draw.text((12, image.height - 29), text, fill=(255, 255, 255), font=font)
        if before:
            try:
                element = self.selenium.find_element(By.XPATH, step['path'])
                rect = element.rect
                x, y = rect['x'] + rect['width'] / 4, rect['y'] - self.selenium.execute_script(
                    'return window.scrollY') + rect['height'] / 2
                draw = ImageDraw.Draw(image)
                draw.polygon([(x, y), (x + 14, y + 20), (x + 5, y + 18), (x, y + 26)], fill=(220, 53, 69))
            except Exception:
                pass
        return image

    def _save_gif(self, frames, name):
        folder = self.results_dir / 'gif'
        folder.mkdir(parents=True, exist_ok=True)
        frames[0].save(folder / ('%s.gif' % _slug(name)), save_all=True, append_images=frames[1:],
                       duration=900, loop=0, optimize=False)
