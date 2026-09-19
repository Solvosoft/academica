"""Selectores compartidos por las historias."""

# --- select2 ------------------------------------------------------------------
SELECT2_SEARCH = "//span[contains(@class,'select2-container--open')]//*[contains(@class,'select2-search__field')]"
SELECT2_REAL_RESULT = ("//li[contains(@class,'select2-results__option')]"
                       "[not(contains(@class,'loading-results'))]"
                       "[not(contains(@class,'select2-results__message'))][not(ul)]")


def select2_result(index=1):
    # Los paréntesis son necesarios: primero se filtra, después se indexa.
    return "(%s)[%d]" % (SELECT2_REAL_RESULT, index)


def select2_inline_search(field_id):
    return ("//*[@id='%s']/following-sibling::span//*[contains(@class,'select2-search__field')]"
            % field_id)


def select2_field(field_id):
    return ("//*[@id='%s']/following-sibling::span//span[contains(@class,'select2-selection')]"
            % field_id)


# --- genéricos ----------------------------------------------------------------
def text(value):
    """Cualquier elemento visible cuyo texto contiene ``value``."""
    return "//*[not(self::script)][contains(normalize-space(.), %s)][not(*[contains(normalize-space(.), %s)])]" % (
        _q(value), _q(value))


def link(value):
    return "//a[contains(normalize-space(.), %s)]" % _q(value)


def button(value):
    return ("//button[contains(normalize-space(.), %s)] | //input[(@type='submit' or @type='button')"
            " and contains(@value, %s)]" % (_q(value), _q(value)))


def field(name):
    return "//*[@name='%s']" % name


def by_id(element_id):
    return "//*[@id='%s']" % element_id


def message(value):
    """Mensaje de Django (gentelella/app/messages.html)."""
    return "//ul[contains(@class,'messages')]/li[contains(normalize-space(.), %s)]" % _q(value)


def _q(value):
    if "'" not in value:
        return "'%s'" % value
    return 'concat(%s)' % ", \"'\", ".join("'%s'" % part for part in value.split("'"))


# --- modales y alertas ----------------------------------------------------------
DELETE_MODAL_CONFIRM = "//div[contains(@class,'modal') and contains(@class,'show')]//a[@id='deleteitem']"
SWAL_POPUP = "//div[contains(@class,'swal2-popup')]"
SWAL_CONFIRM = "//button[contains(@class,'swal2-confirm')]"


def swal_title(value):
    return "//*[contains(@class,'swal2-title') and contains(normalize-space(.), %s)]" % _q(value)


def modal_open(modal_id):
    return "//div[@id='%s' and contains(@class,'show')]" % modal_id


def modal_closed(modal_id):
    return "//div[@id='%s' and not(contains(@class,'show'))]" % modal_id


def modal_save(modal_id):
    """Botón "Guardar" de los modales ObjectCRUD de djgentelella."""
    return "//div[@id='%s']//button[contains(@class,'formadd')]" % modal_id


# --- ObjectCRUD de djgentelella (catálogos) ------------------------------------
def gt_crud_table_ready(table_id):
    return "//table[@id='%s']/tbody/tr" % table_id


def gt_crud_row_action(table_id, row_text, action_icon):
    return ("//table[@id='%s']//tr[td[contains(normalize-space(.), %s)]]"
            "//*[contains(@class,'%s')]" % (table_id, _q(row_text), action_icon))


# --- marcadores de pantalla (una por página; nunca usar //body) -------------------
PAGE_LOGIN = "//input[@name='username']"
PAGE_REGISTER = "//form//input[@id='id_password']/ancestor::form//input[@id='id_email']"
PAGE_BILLS = "//h1[contains(normalize-space(.), 'Pagos Pendientes') or contains(normalize-space(.), 'Unpaid bills')]"
PAGE_MY_COURSES = "//*[contains(normalize-space(.), 'Cursos Pre-Inscritos')]"


def datatable_page(number):
    """Botón de página del paginador de DataTables 2 (Bootstrap 5)."""
    return "//li[contains(@class,'dt-paging-button')]/*[normalize-space(.)='%s']" % number
