"""Verifica que el entorno puede correr las pruebas de navegación (make check-selenium)."""
import importlib
import os
import shutil
import subprocess
import sys

ok = True


def report(name, success, detail=''):
    global ok
    ok = ok and success
    print("[%s] %s %s" % ('OK' if success else 'FALTA', name, detail))


for module in ('django', 'selenium', 'tblib', 'PIL'):
    try:
        mod = importlib.import_module(module)
        report(module, True, getattr(mod, '__version__', ''))
    except ImportError:
        report(module, False, '(make setup)')

browser = next((shutil.which(b) for b in ('chromium', 'google-chrome', 'chromium-browser') if shutil.which(b)), None)
report('navegador', bool(browser), browser or '(instalar chromium)')
driver = os.getenv('CHROMEDRIVER_PATH') or shutil.which('chromedriver')
if driver:
    version = subprocess.run([driver, '--version'], capture_output=True, text=True, timeout=20).stdout.strip()
    report('chromedriver', True, version)
else:
    report('chromedriver', False, '(instalar chromium-driver)')
report('xvfb-run', bool(shutil.which('xvfb-run')), '(apt install xvfb)' if not shutil.which('xvfb-run') else '')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academica.test_settings')
try:
    import django
    django.setup()
    from django.db import connection
    connection.ensure_connection()
    report('PostgreSQL', True, connection.settings_dict['HOST'] + ':' + str(connection.settings_dict['PORT']))
except Exception as exc:
    report('PostgreSQL', False, '(%s; make services)' % str(exc).splitlines()[0])

sys.exit(0 if ok else 1)
