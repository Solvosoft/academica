from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from matricula.models import Student, Course, Group as GroupUPO, Enroll, Period, Category, \
    MenuItem, Page, Professor, Coupon, FakeGroup, WaitingList


class EnrollAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('enroll_finished', 'enroll_activate'), 'group', 'student', 'bill_created', 'course_status', 'pdf_certificate', 'go_to_one_class')
        }),)

    list_display = ('student', 'group', 'enroll_finished', 'enroll_activate', 'go_to_one_class')
    list_filter = ('enroll_activate', 'enroll_finished', 'group')
    list_editable = ('enroll_activate', 'enroll_finished', 'go_to_one_class')
    actions = ['set_enroll_finished_true', 'set_enroll_activate_true']
    # 'enroll_date'

    def set_enroll_activate_true(self, request, queryset):
        queryset.update(enroll_activate=True)
    set_enroll_activate_true.short_description = _("Active user for enrollment")

    def set_enroll_finished_true(self, request, queryset):
        queryset.update(enroll_finished=True)
    set_enroll_finished_true.short_description = _("Active user for pre-enrollment")


admin.site.register(Student)
admin.site.register(Coupon)
admin.site.register(Course)
admin.site.register(GroupUPO)
admin.site.register(Enroll, EnrollAdmin)
admin.site.register(Period)
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Page)
admin.site.register(Professor)
admin.site.register(FakeGroup)
admin.site.unregister(Group)
admin.site.register(WaitingList)
admin.site.site_header = _("Academica administrator site")
