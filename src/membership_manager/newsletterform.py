from async_notifications.interfaces import NewsLetterInterface
from membership_manager.forms import OrganizationForm


class MembershipManager(NewsLetterInterface):
    name = "membresia"

    def get_form(self):
        pass

    def set_form(self, form):
        self.form = form

    def get_queryset(self):
        pass

    def get_emails(self):
        pass

class ContactManager(NewsLetterInterface):
    name = "contacto"

class OrganizationManager(NewsLetterInterface):
    name = "organizacion"

    def get_form(self):
        return OrganizationForm()


class InvoiceManager(NewsLetterInterface):
    name = "factura"