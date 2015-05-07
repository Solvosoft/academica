from django.contrib import admin
from matricula.models import Student, Course, Group, Enroll

# Register your models here.

class EnrollAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('enroll_finished', 'enroll_activate'), 'group', 'student')
        }),)

    list_display = ('student', 'group', 'enroll_finished', 'enroll_activate')
    list_filter = ('enroll_activate', 'enroll_finished', 'group')
    list_editable = ('enroll_activate', 'enroll_finished')
    actions = ['set_enroll_finished_true', 'set_enroll_activate_true']
    # 'enroll_date'

    def set_enroll_activate_true(self, request, queryset):
        queryset.update(enroll_activate=True)
    set_enroll_activate_true.short_description = "Active user for enrollment"

    def set_enroll_finished_true(self, request, queryset):
        queryset.update(enroll_finished=True)
    set_enroll_finished_true.short_description = "Active user for pre-enrollment"

    
class GroupAdmin(admin.ModelAdmin):
    fieldsets = (
                (None, {'classes': ('wide', 'extrapretty'),
                        'fields': ('course', 'name', 'schedule',
                                    ('pre_enroll_start', 'pre_enroll_finish'),
                                    ('enroll_start' , 'enroll_finish'))
                        }),
                )
admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Group, GroupAdmin)
admin.site.register(Enroll, EnrollAdmin)
