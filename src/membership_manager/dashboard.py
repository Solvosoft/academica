from djgentelella.elements import StatsElement, StatsCountList

from async_notifications.models import NewsLetter
from membership_core.models import Country
from membership_manager.models import Membership, Invoice, Organization
from membership_manager.utils import check_newsletter_update


class MembresiasActivasStats(StatsElement):
    def get_top_icon(self):
        return "fa fa-list-alt"

    def get_top_text(self):
        return " Membresias Activas"

    def get_count(self):
        return Membership.objects.filter(state='active').count()

    def get_count_color(self):
        return 'green'

    def get_bottom_color(self):
        return "red"

    def get_bottom_text(self):
        return "inactivas"

    def get_bottom_icon(self):
        return "fa fa-sort-desc"

    def get_bottom_icon_text(self):
        return Membership.objects.filter(state='inactive').count()


class FacturasStats(StatsElement):
    def get_top_icon(self):
        return "fa fa-credit-card"

    def get_top_text(self):
        return " Facturas pagas"

    def get_count(self):
        return Invoice.objects.filter(status='paid').count()

    def get_count_color(self):
        return 'green'

    def get_bottom_color(self):
        return "red"

    def get_bottom_text(self):
        return " Pendientes"

    def get_bottom_icon(self):
        return "fa fa-sort-desc"

    def get_bottom_icon_text(self):
        return Invoice.objects.filter(status='pending').count()


class PaisesStats(StatsElement):
    def get_top_icon(self):
        return "fa fa-globe"

    def get_top_text(self):
        return " Organizaciones"

    def get_count(self):
        return Organization.objects.filter(active=True, type=False).count()

    def get_count_color(self):
        return 'green'

    def get_bottom_color(self):
        return "green"

    def get_bottom_text(self):
        return " Países"

    def get_bottom_icon(self):
        return "fa fa-sort-asc"

    def get_bottom_icon_text(self):
        return Country.objects.all().count()


class UpdateNewsLetter(StatsElement):
    def render(self):
        dev = "<a type='button' class='btn btn-success' id='update_news_letter' style='margin-top: 10%;'>Actualizar boletines</a>"
        return dev


def update_news_letter_emails():
    news_letter_list = NewsLetter.objects.all()
    add_update_button = False

    for news_letter in news_letter_list:
        if check_newsletter_update(news_letter):
            add_update_button = True
            break
    return add_update_button

class TopStats(StatsCountList):

    stats_views = [MembresiasActivasStats, FacturasStats, PaisesStats]

    if update_news_letter_emails():
        stats_views = [MembresiasActivasStats, FacturasStats, PaisesStats, UpdateNewsLetter]