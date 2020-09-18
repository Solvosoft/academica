from djgentelella.elements import StatsElement, StatsCountList

from membership_manager.models import Membership


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


class TopStats(StatsCountList):
    stats_views = [MembresiasActivasStats]
