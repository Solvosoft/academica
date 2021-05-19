# encoding: utf-8
'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import url
from django.urls import path
from matricula.models import WaitingList

from matricula.views.Auth import recover_password, \
    mail_recover_pass, authenticate, create_user, login_user, \
    confirm_email, logout, StudentEdit, add_student
from matricula.views.Courses import list_courses, view_course, course_detail
from matricula.views.Enrollments import list_enroll, enrollme, \
    finish_enroll
from matricula.views.Pages import PageDetail
from .admin import admin_site
from .views.admin_views import CategoryList, GroupDetailView, create_category, \
    CategoryDelete, edit_category, CourseList, create_course, \
    CourseDelete, edit_course, MenuItemList, create_menuitem, MenuItemDelete, \
    edit_menuitem, PeriodList, create_period, edit_period, PeriodDelete, \
    GroupList, create_group, edit_group, GroupDelete, EnrollList, \
    create_enroll, edit_enroll, EnrollDelete, StudentList, create_student, \
    edit_student, StudentDelete, PageList, create_page, edit_page, PageDelete, \
    export_group, recovery_pass_student, MenuPageDelete, create_menupage, \
    pre_enroll_group, add_group_course, list_students_group, \
    export_enrolled_group, open_group, close_group, regenerate_certificate, \
    build_pdf_certificate_list, edit_password_student, \
    StudentDetailView

from .views.coupons_views import coupons_list, create_cupon, delete_coupon, edit_coupon, coupons_bill_list, \
    add_coupons_group
from matricula.contrib.bills.urls import urlpatterns as billurls
from matricula.views.Auth import get_profile

from .views.professor_views import AddUser, ProfessorsList, CreateProfessor, EditProfessor, edit_profile, delete_professor, \
    deactivate_professor
from .views.students_views import qualify_students, update_enroll, update_enroll_status, GradeList

urlpatterns = [
    url('enrrolment/accounts/profile/?$', get_profile, name='profile'),
    url('^student/history/$', GradeList.as_view(), name='student_history'),
    url('enrrolment/create_user$', create_user, name="create_user_academy"),
    url('enrrolment/add_student$', add_student, name="add_student"),
    url('enrrolment/login_user$', login_user, name="login_user"),
    url('enrrolment/confirm_email$', confirm_email, name="confirm_email"),
    url('enrrolment/authenticate$', authenticate, name="authenticate"),
    url('enrrolment/logout$', logout, name="logout"),
    url('recover_password$', recover_password, name="recover_password"),
    url('enrrolment/mail_recover_pass$', mail_recover_pass, name='mail_recover_pass'),
    url('enrrolment/user/profile/(?P<pk>[0-9]+)/$', StudentEdit.as_view(),
        name='myprofile'),
    url('enrrolment/courses_list$', list_courses, name='courses'),
    url('enrrolment/course/(?P<pk>\\d+)$', view_course, name='course'),
    url('enrrolment/course$', view_course, name='course_list'),
    url('enrrolment/enrollme/(?P<pk>\\d+)$', enrollme, name="enrollme"),
    url('enrrolment/enrollment$', list_enroll, name="enrollment"),
    url('enrrolment/finish_enroll/(?P<pk>\\d+)$', finish_enroll, name="finish_enroll"),
    url(r'enrrolment_pages/(?P<pk>\d+)$', PageDetail.as_view(), name="academica_pages"),
    path('enrrolment_pages/<slug:slug>', PageDetail.as_view(), name="pages_view"),
    url('enrrolment/categories', CategoryList.as_view(), name="categories"),
    url('enrrolment/create_category', create_category, name="create_category"),
    path('enrrolment/delete_category/<int:pk>/', CategoryDelete.as_view() , name="delete_category"),
    path('enrrolment/edit_category/<int:pk>/', edit_category, name="edit_category"),
    url('enrrolment/courses', CourseList.as_view(), name="enrrolment_courses"),
    path('enrrolment_course_detail/<int:pk>/', course_detail, name="course_detail"),
    url('enrrolment/create_course/', create_course, name="create_course"),
    path('enrrolment/add_group_course/<int:pk>/', add_group_course, name="add_group_course"),
    path('enrrolment/delete_course/<int:pk>/', CourseDelete.as_view(), name="delete_course"),
    path('enrrolment_edit_course/<int:pk>/', edit_course, name="edit_course"),
    url('enrrolment/menuitems', MenuItemList.as_view(), name="menuitems"),
    url('enrrolment/create_menuitem', create_menuitem, name="create_menuitem"),
    path('enrrolment/delete_menuitem/<int:pk>/', MenuItemDelete.as_view() , name="delete_menuitem"),
    path('enrrolment/edit_menuitem/<int:pk>/', edit_menuitem, name="edit_menuitem"),
    url('enrrolment/periods', PeriodList.as_view(), name="periods"),
    url('enrrolment/create_period', create_period, name="create_period"),
    path('enrrolment/delete_period/<int:pk>/', PeriodDelete.as_view() , name="delete_period"),
    path('enrrolment/edit_period/<int:pk>/', edit_period, name="edit_period"),
    url('enrrolment/groups', GroupList.as_view(), name="groups_enroll"),
    path('enrrolment/<int:pk>/waitinglist', GroupDetailView.as_view(), name="waitinglist_group"),
    path('enrrolment/pre_enroll_group/<int:pk>/', pre_enroll_group, name="pre_enroll_group"),
    url('enrrolment/create_group', create_group, name="create_group_enroll"),
    path('enrrolment/delete_group/<int:pk>/', GroupDelete.as_view(), name="delete_group_enroll"),
    path('enrrolment/edit_group/<int:pk>/', edit_group, name="edit_group_enroll"),
    path('enrrolment/open_group/<int:pk>/', open_group, name="open_group"),
    path('enrrolment/close_group/<int:pk>/', close_group, name="close_group"),
    path('enrrolment/export_group/<int:pk>/', export_group, name="export_group"),
    path('enrrolment/list_students_group/<int:pk>/', list_students_group, name="list_students_group"),
    path('enrrolment/export_enrolled_group/<int:pk>/', export_enrolled_group, name="export_enrolled_group"),
    url('enrrolment/enrolls', EnrollList.as_view(), name="enrolls"),
    url('enrrolment/create_enroll', create_enroll, name="create_enroll"),
    path('enrrolment/delete_enroll/<int:pk>/', EnrollDelete.as_view(), name="delete_enroll"),
    path('enrrolment/edit_enroll/<int:pk>/', edit_enroll, name="edit_enroll"),
    url('enrrolment/students', StudentList.as_view(), name="students"),
    path('enrrolment/<int:pk>/qualify_students', qualify_students, name="qualify_students"),
    path('enrrolment/recovery_pass_student/<int:pk>/', recovery_pass_student, name="recovery_pass_student"),
    url('enrrolment/create_student', create_student, name="create_student"),
    path('enrrolment/delete_student/<int:pk>/', StudentDelete.as_view(), name="delete_student"),
    path('enrrolment/edit_student/<int:pk>/', edit_student, name="edit_student"),
    path('enrrolment/edit_password_student/<int:pk>/', edit_password_student, name="change_password_student"),
    path('enrrolment/student/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    url('enrrolment/pages', PageList.as_view(), name="pages"),
    url('enrrolment/create_page', create_page, name="create_page"),
    path('enrrolment/create_menupage/<int:pk>/', create_menupage, name="create_menupage"),
    path('enrrolment/delete_menu_page/<int:pk>/', MenuPageDelete.as_view(), name="delete_menupage"),
    path('enrrolment/delete_page/<int:pk>/', PageDelete.as_view() , name="delete_page"),
    path('enrrolment_edit_page/<int:pk>', edit_page, name="edit_page"),
    path('enrrolment/profile/', edit_profile, name="edit_profile"),
    path('enrrolment/edit_professor/<int:pk>/', EditProfessor.as_view(), name="edit_professor"),
    path('enrrolment/create_professor/', CreateProfessor.as_view(), name="create_professor"),
    path('enrrolment/delete_professor/<int:pk>/', delete_professor, name="delete_professor"),
    path('enrrolment/deactivate_professor/<int:pk>/', deactivate_professor, name="deactivate_professor"),
    path('enrrolment/professors/', ProfessorsList.as_view(), name="professors_list"),
    path('enrrolment/json/students/', update_enroll, name='update_enroll'),
    path('enrrolment/<int:pk>/qualify_students/<str:status>/', update_enroll_status, name="qualify_students_status"),
    path('enrrolment/coupons/', coupons_list, name="coupons_list"),
    path('enrrolment/coupons/<int:pk>/bill', coupons_bill_list, name="coupons_bill_list"),
    path('enrrolment/coupons/create', create_cupon, name="create_cupon"),
    path('enrrolment/coupons/<int:pk>/delete', delete_coupon, name="delete_cupon"),
    path('enrrolment/coupons/<int:pk>/edit', edit_coupon, name="edit_coupon"),
    path('enrrolment/coupons/<int:pk>/<int:percentage>/group/', add_coupons_group, name="add_coupons_group"),
    path('enrrolment_certificate/build/<int:pk>/', build_pdf_certificate_list, name="build_pdf_certificate_list"),
    path('enrrolment_certificate_enroll/<int:pk_group>/<int:pk>/', regenerate_certificate, name="build_pdf_certificate_view"),
    path('enrollment/users/create', AddUser.as_view(), name="create_simple_user"),
] + billurls
