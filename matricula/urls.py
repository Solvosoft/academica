# encoding: utf-8
'''
Created on 7/4/2015

@author: luisza
'''

from django.conf.urls import url
from django.urls import path
from matricula.views.Auth import recover_password,\
    mail_recover_pass, authenticate, create_user, login_user,\
    confirm_email, logout, StudentEdit
from matricula.views.Courses import list_courses, view_course
from .admin import admin_site
from matricula.views.Pages import PageDetail
from matricula.views.Enrollments import list_enroll, enrollme,\
    finish_enroll
from .views.admin_views import CategoryList, create_category,\
    show_category, CategoryDelete, edit_category, CourseList,\
    create_course, show_course, CourseDelete, edit_course

urlpatterns = [
    url('^create_user$', create_user, name="create_user"),
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
    path('enrrolment/show_category/<int:pk>/', show_category, name="show_category"),
    path('enrrolment/delete_category/<int:pk>/', CategoryDelete.as_view() , name="delete_category"),
    path('enrrolment/edit_category/<int:pk>/', edit_category, name="edit_category"),
    url('enrrolment/courses', CourseList.as_view(), name="enrrolment_courses"),
    url('enrrolment/create_course', create_course, name="create_course"),
    path('enrrolment/show_course/<int:pk>/', show_course, name="show_course"),
    path('enrrolment/delete_course/<int:pk>/', CourseDelete.as_view() , name="delete_course"),
    path('enrrolment/edit_course/<int:pk>/', edit_course, name="edit_course"),
]
