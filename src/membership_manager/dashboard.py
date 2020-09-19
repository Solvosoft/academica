from djgentelella.elements import StatsElement, StatsCountList

from membership_core.models import Country
from membership_manager.models import Membership, Invoice, Organization


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
        return Organization.objects.filter(active=True).count()

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



class TopStats(StatsCountList):
    stats_views = [MembresiasActivasStats, FacturasStats, PaisesStats]
