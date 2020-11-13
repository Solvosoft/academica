# encoding: utf-8
'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import url
from django.urls import path
from matricula.views.Auth import recover_password,\
    mail_recover_pass, authenticate, create_user, login_user,\
    confirm_email, logout, StudentEdit, add_student
from matricula.views.Courses import list_courses, view_course
from .admin import admin_site
from matricula.views.Pages import PageDetail
from matricula.views.Enrollments import list_enroll, enrollme,\
    finish_enroll
from .views.admin_views import CategoryList, create_category,\
    CategoryDelete, edit_category, CourseList, create_course,\
    CourseDelete, edit_course, MenuItemList, create_menuitem, MenuItemDelete,\
    edit_menuitem, PeriodList, create_period, edit_period, PeriodDelete,\
    GroupList, create_group, edit_group, GroupDelete, EnrollList,\
    create_enroll, edit_enroll, EnrollDelete, StudentList, create_student,\
    edit_student, StudentDelete, PageList, create_page, edit_page, PageDelete,\
    export_group, recovery_pass_student, MenuPageDelete, create_menupage,\
    pre_enroll_group, add_group_course, list_students_group,\
    export_enrolled_group
from matricula.contrib.bills.urls import urlpatterns as billurls

urlpatterns = [
    url('^create_user$', create_user, name="create_user"),
    url('^add_student$', add_student, name="add_student"),
    url('^login_user$', login_user, name="login_user"),
    url('^confirm_email$', confirm_email, name="confirm_email"),
    url('^authenticate$', authenticate, name="authenticate"),
    url('^logout$', logout, name="logout"),
    url('^recover_password$', recover_password, name="recover_password"),
    url('^mail_recover_pass$', mail_recover_pass, name='mail_recover_pass'),
    url('^user/profile/(?P<pk>[0-9]+)/$', StudentEdit.as_view(),
        name='myprofile'),
    url('^courses$', list_courses, name='courses'),
    url('^course/(?P<pk>\\d+)$', view_course, name='course'),
    url('^enrollme/(?P<pk>\\d+)$', enrollme, name="enrollme"),
    url('^enrollment$', list_enroll, name="enrollment"),
    url('^finish_enroll/(?P<pk>\\d+)$', finish_enroll, name="finish_enroll"),
    url(r'^admin/', admin_site.urls),
    url(r'^pages/(?P<pk>\d+)$', PageDetail.as_view(), name="academica_pages"),
    url('enrrolment/categories', CategoryList.as_view(), name="categories"),
    url('enrrolment/create_category', create_category, name="create_category"),
    path('enrrolment/delete_category/<int:pk>/', CategoryDelete.as_view() , name="delete_category"),
    path('enrrolment/edit_category/<int:pk>/', edit_category, name="edit_category"),
    url('enrrolment/courses', CourseList.as_view(), name="enrrolment_courses"),
    url('enrrolment/create_course', create_course, name="create_course"),
    path('enrrolment/add_group_course/<int:pk>/', add_group_course, name="add_group_course"),
    path('enrrolment/delete_course/<int:pk>/', CourseDelete.as_view(), name="delete_course"),
    path('enrrolment/edit_course/<int:pk>/', edit_course, name="edit_course"),
    url('enrrolment/menuitems', MenuItemList.as_view(), name="menuitems"),
    url('enrrolment/create_menuitem', create_menuitem, name="create_menuitem"),
    path('enrrolment/delete_menuitem/<int:pk>/', MenuItemDelete.as_view() , name="delete_menuitem"),
    path('enrrolment/edit_menuitem/<int:pk>/', edit_menuitem, name="edit_menuitem"),
    url('enrrolment/periods', PeriodList.as_view(), name="periods"),
    url('enrrolment/create_period', create_period, name="create_period"),
    path('enrrolment/delete_period/<int:pk>/', PeriodDelete.as_view() , name="delete_period"),
    path('enrrolment/edit_period/<int:pk>/', edit_period, name="edit_period"),
    url('enrrolment/groups', GroupList.as_view(), name="groups_enroll"),
    path('enrrolment/pre_enroll_group/<int:pk>/', pre_enroll_group, name="pre_enroll_group"),
    url('enrrolment/create_group', create_group, name="create_group_enroll"),
    path('enrrolment/delete_group/<int:pk>/', GroupDelete.as_view(), name="delete_group_enroll"),
    path('enrrolment/edit_group/<int:pk>/', edit_group, name="edit_group_enroll"),
    path('enrrolment/export_group/<int:pk>/', export_group, name="export_group"),
    path('enrrolment/list_students_group/<int:pk>/', list_students_group, name="list_students_group"),
    path('enrrolment/export_enrolled_group/<int:pk>/', export_enrolled_group, name="export_enrolled_group"),
    url('enrrolment/enrolls', EnrollList.as_view(), name="enrolls"),
    url('enrrolment/create_enroll', create_enroll, name="create_enroll"),
    path('enrrolment/delete_enroll/<int:pk>/', EnrollDelete.as_view() , name="delete_enroll"),
    path('enrrolment/edit_enroll/<int:pk>/', edit_enroll, name="edit_enroll"),
    url('enrrolment/students', StudentList.as_view(), name="students"),
    path('enrrolment/recovery_pass_student/<int:pk>/', recovery_pass_student, name="recovery_pass_student"),
    url('enrrolment/create_student', create_student, name="create_student"),
    path('enrrolment/delete_student/<int:pk>/', StudentDelete.as_view() , name="delete_student"),
    path('enrrolment/edit_student/<int:pk>/', edit_student, name="edit_student"),
    url('enrrolment/pages', PageList.as_view(), name="pages"),
    url('enrrolment/create_page', create_page, name="create_page"),
    path('enrrolment/create_menupage/<int:pk>/', create_menupage, name="create_menupage"),
    path('enrrolment/delete_menu_page/<int:pk>/', MenuPageDelete.as_view(), name="delete_menupage"),
    path('enrrolment/delete_page/<int:pk>/', PageDelete.as_view() , name="delete_page"),
    path('enrrolment/edit_page/<int:pk>/', edit_page, name="edit_page"),
] + billurls
