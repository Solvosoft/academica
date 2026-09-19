"""
Inyecta en cada página HTML un script que indica cuándo está lista.

- ``body[data-test-ready="true"]`` cuando el DOM cargó y las tablas DataTables
  con ajax terminaron su primera carga.
- ``window.__testPendingDT`` cuenta las peticiones ajax de DataTables en curso.

Solo se instala con ``academica.test_settings``; producción no lo ve.
"""
READY_SCRIPT = b"""
<script>
(function () {
  var pendingInit = 0, domReady = false;
  window.__testPendingDT = 0;
  function checkReady() {
    if (domReady && pendingInit === 0 && document.body) {
      document.body.setAttribute('data-test-ready', 'true');
    }
  }
  if (window.jQuery) {
    jQuery(document).on('preXhr.dt', function () { window.__testPendingDT++; });
    jQuery(document).on('xhr.dt', function () {
      window.__testPendingDT = Math.max(0, window.__testPendingDT - 1);
      checkReady();
    });
    jQuery(document).on('preInit.dt', function (e, settings) {
      if (settings.ajax) {
        pendingInit++;
        jQuery(e.target).one('xhr.dt', function () { pendingInit--; checkReady(); });
      }
    });
    jQuery(function () { setTimeout(function () { domReady = true; checkReady(); }, 0); });
  } else {
    document.addEventListener('DOMContentLoaded', function () { domReady = true; checkReady(); });
  }
})();
</script>
"""


class TestingReadyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get('Content-Type', '')
        if (not getattr(response, 'streaming', False) and content_type.startswith('text/html')
                and b'</body>' in response.content):
            response.content = response.content.replace(b'</body>', READY_SCRIPT + b'</body>', 1)
            if response.has_header('Content-Length'):
                response['Content-Length'] = str(len(response.content))
        return response
