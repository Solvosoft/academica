# encoding: utf-8

from django.contrib import admin
from matricula.models import Student, Course, Group, Enroll, Period, Category, \
    MenuItem, Page, MultilingualContent, MenuTranslations
from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url
from django.urls import reverse
from django.utils.html import format_html
from matricula.admins import BaseGroup
from django_ajax.decorators import ajax

from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from matricula.forms import MenuItemFormPage

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


class GroupAdmin(admin.ModelAdmin, BaseGroup):
    fieldsets = (
                (None, {'classes': ('wide', 'extrapretty'),
                        'fields': (('period', 'course', 'student_list_ref'),
                                   'name', 'maximum',
                                   ('cost', 'currency'), 'schedule',
                                    'flow',
                                    ('pre_enroll_start', 'pre_enroll_finish'),
                                    ('enroll_start' , 'enroll_finish'))
                        }),
                )
    list_display = ('name', 'course', 'period', 'maximum',
                    'pre_enroll_start', 'pre_enroll_finish', 'count_student_preenroll',
                    'count_student_enroll', 'payments')

    list_filter = ('period',)
    ordering = ('pre_enroll_start',)
    actions = ['action_copy_last_period', 'action_open_group']
    search_fields = ('course__name',)
    readonly_fields = ('student_list_ref',)

    def student_list_ref(self, obj=None):
        if obj.pk is None:
            return _("Student list don't exist yet")

        return format_html('<a href={}> List of students</a>',
                           reverse('admin:student_list', kwargs={'pk': obj.pk})
                           )

    student_list_ref.short_description = _("List students")

    def count_student_preenroll(self, obj):
        # return obj.enroll_set.filter(enroll_finished=False).count()
        return format_html('<a href={}>{}</a>',
                           reverse('admin:student_list', kwargs={'pk': obj.pk}),
                           obj.enroll_set.count()
                          )
    count_student_preenroll.short_description = _("# student pre-enroll")

    def count_student_enroll(self, obj):
        return format_html('<a href={}?enroll=1>{}</a>',
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
            url(r'^open_group/(?P<pk>\d+)$', self.admin_site.admin_view(ajax(self.open_group)),
                name="open_group"),
            url(r'^close_group/(?P<pk>\d+)$', self.admin_site.admin_view(ajax(self.close_group)),
                name="close_group"),
            url(r'^export_pdf/(?P<pk>\d+)$', self.admin_site.admin_view(self.export_pdf),
                name="export_pdf"),

        ]

        return my_urls + urls



class MyUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        if request.user.is_superuser:
            perm_fields = ('is_active', 'is_staff', 'is_superuser',
                           'groups', 'user_permissions')
        else:
            # modify these to suit the fields you want your
            # staff user to be able to edit
            perm_fields = ('is_active', 'is_staff')

        return [(None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
                (_('Permissions'), {'fields': perm_fields}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')})]


class MenuInline(admin.StackedInline):
    model = MenuTranslations
    extra = 1


class MenuItemAdmin(admin.ModelAdmin):
    obj = None
    inlines = [MenuInline]

    def get_form(self, request, obj=None, **kwargs):
        self.obj = obj
        if obj is None or obj.type == 1:
            kwargs['form'] = MenuItemFormPage
        return super(MenuItemAdmin, self).get_form(request, obj, **kwargs)

    def get_changeform_initial_data(self, request):
        dev = {"type": 1}
        return dev


class PageInline(admin.TabularInline):
    model = MultilingualContent
    extra = 1


class PageAdmin(admin.ModelAdmin):
    inlines = [PageInline]

class MenuAdmin(admin.ModelAdmin):
    inlines = [MenuInline]

admin.site.register(Student, MyUserAdmin)
admin.site.register(Course)
admin.site.register(Group, GroupAdmin)
admin.site.register(Enroll, EnrollAdmin)
admin.site.register(Period)
admin.site.register(Category)
admin.site.register(MenuItem, MenuAdmin)
admin.site.register(Page, PageAdmin)

admin.site.site_header = _("Academica administrator site")


admin_site = AdminSite(name='matricula_admin')
admin_site.site_header = _("Academica administrator site")


admin_site.register(Student, MyUserAdmin)
admin_site.register(Course)
admin_site.register(Group, GroupAdmin)
admin_site.register(Enroll, EnrollAdmin)
admin_site.register(Period)
admin_site.register(Category)
admin_site.register(MenuItem, MenuItemAdmin)
admin_site.register(Page, PageAdmin)
