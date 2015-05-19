from django.contrib import admin
from matricula.models import Student, Course, Group, Enroll, Period, Category
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.html import format_html

# Register your models here.

class EnrollAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('enroll_finished', 'enroll_activate'), 'group', 'student', 'bill_created')
        }),)

    list_display = ('student', 'group', 'enroll_finished', 'enroll_activate')
    list_filter = ('enroll_activate', 'enroll_finished', 'group')
    list_editable = ('enroll_activate', 'enroll_finished')
    actions = ['set_enroll_finished_true', 'set_enroll_activate_true']
    # 'enroll_date'

    def set_enroll_activate_true(self, request, queryset):
        queryset.update(enroll_activate=True)
    set_enroll_activate_true.short_description = _("Active user for enrollment")

    def set_enroll_finished_true(self, request, queryset):
        queryset.update(enroll_finished=True)
    set_enroll_finished_true.short_description = _("Active user for pre-enrollment")

    
class GroupAdmin(admin.ModelAdmin):
    fieldsets = (
                (None, {'classes': ('wide', 'extrapretty'),
                        'fields': ('period', 'course', 'name', 'maximum', 'cost', 'schedule',
                                    ('pre_enroll_start', 'pre_enroll_finish'),
                                    ('enroll_start' , 'enroll_finish'))
                        }),
                )
    list_display = ('name', 'course', 'period', 'maximum', 'count_student_preenroll',
                    'count_student_enroll', 'payments')
    list_filter = ('period',)
    ordering = ('pre_enroll_start',)

    def count_student_preenroll(self, obj):
        return obj.enroll_set.filter(enroll_finished=False).count()
    count_student_preenroll.short_description = _("# student pre-enroll")

    def count_student_enroll(self, obj):

        return format_html('<a href={}>{}</a>',
                           reverse('admin:student_list', kwargs={'pk': obj.pk}),
                           obj.enroll_set.filter(enroll_finished=True).count()
                           )

    count_student_enroll.allow_tags = True
    count_student_enroll.short_description = _("# student enroll")

    def payments(self, obj):
        return obj.cost * obj.enroll_set.filter(enroll_finished=True).count() 
    payments.short_description = _("Total cash")

    def get_urls(self):
        urls = super(GroupAdmin, self).get_urls()
        my_urls = [
            url(r'^student_list/(?P<pk>\d+)$', self.admin_site.admin_view(self.student_list),
                name="student_list"),
        ]
        return my_urls + urls

    def student_list(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        context = dict(
           # Include common variables for rendering the admin template.
           self.admin_site.each_context(request),
           group=group,
           title=_('Student List')
        )
        
        return TemplateResponse(request, "student_list.html", context)

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(Group, GroupAdmin)
admin.site.register(Enroll, EnrollAdmin)
admin.site.register(Period)
admin.site.register(Category)

admin.site.site_header = "Academica administrator"
