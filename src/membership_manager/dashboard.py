from djgentelella.elements import StatsElement, StatsCountList
from membership_core.models import Country
from matricula.models import Enroll, Student
from django.utils.translation import gettext as _


class StudentStats(StatsElement):
    def get_top_icon(self):
        return "fa fa-list-alt"

    def get_top_text(self):
        return _("Active students")

    def get_count(self):
        return Student.objects.count()

    def get_count_color(self):
        return 'green'

    def get_bottom_color(self):
        return "red"

    def get_bottom_text(self):
        return _("Inactive")

    def get_bottom_icon(self):
        return "fa fa-sort-desc"

    def get_bottom_icon_text(self):
        return Student.objects.filter(user__is_active=False).count()


class EnrollStats(StatsElement):
    def get_top_icon(self):
        return "fa fa-credit-card"

    def get_top_text(self):
        return _("Enroll approved")

    def get_count(self):
        return Enroll.objects.filter(course_status="approved").count();

    def get_count_color(self):
        return 'green'

    def get_bottom_color(self):
        return "red"

    def get_bottom_text(self):
        return _("Fail")

    def get_bottom_icon(self):
        return "fa fa-sort-desc"

    def get_bottom_icon_text(self):
        return Enroll.objects.filter(course_status="reproved").count();


class CountryStats(StatsElement):
    def get_top_icon(self):
        return "fa fa-globe"

    def get_top_text(self):
        return _("Countries")

    def get_count(self):
        return Country.objects.all().count()

    def get_count_color(self):
        return 'green'

    def get_bottom_color(self):
        return "green"

    def get_bottom_text(self):
        return _("Countries")

    def get_bottom_icon(self):
        return "fa fa-sort-asc"

    def get_bottom_icon_text(self):
        return Student.objects.values('country__pk').distinct().count()


class TopStats(StatsCountList):
    stats_views = [StudentStats, EnrollStats, CountryStats]
