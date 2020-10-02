from django.contrib.auth.decorators import login_required, permission_required
from django.urls import path

from membership_manager.reports.view import reports, add_reporttype_view, download_graph, show_report, list_report, \
    filters_extra
from membership_manager.views import OrganizationView, ContactListView, MembershipListView, delete_membership_service, \
    create_membership, edit_membership, delete_memberships, create_contacts
from membership_manager.views import create_news_letter_membership, \
    create_email_notification, email_template
from . import views
from .news_letter import news_letter_list, create_news_letter, send_news_letter, delete_news_letter, EditNewsLetter, \
    delete_task, create_news_letter_template, create_task

organization_view = OrganizationView()
urlpatterns = [
    path('home/', views.index, name="home"),
    path('contacts/', permission_required(
        'membership_manager.view_contact')(ContactListView.as_view()), name="contacts"),
    path('contacts/create', create_contacts, name="create_contacts"),
    path('organizations/', login_required(MembershipListView.as_view()), name="organizations"),
    path('memberships/', permission_required(
        'membership_manager.view_membership')(MembershipListView.as_view()), name="memberships"),
    path(
        'membership/delete_service/<int:pk>/', delete_membership_service,
        name="delete_membership_service"),
    path('memberships/create', create_membership, name="create_memberships"),
    path('memberships/edit/<int:pk>', edit_membership, name="edit_memberships"),
    path('memberships/delete/<int:pk>/', delete_memberships, name="delete_memberships"),
    path('newsletter/', news_letter_list, name="news_letter_list"),
    path('newsletter/create/<int:pk>/', create_news_letter, name="create_news_letter"),
    path('newsletter/send/<int:pk>/', send_news_letter, name="send_news_letter"),
    path('newsletter/delete/<int:pk>/', delete_news_letter, name="delete_news_letter"),
    path('newsletter/edit/<int:pk>/', EditNewsLetter.as_view(), name="edit_news_letter"),
    path('task/create/<int:pk>/', create_task, name="create_task"),
    path('task/delete/<int:pk>/', delete_task, name="delete_task"),
    path('newslettertemplate/create/', create_news_letter_template, name="create_news_letter_template"),
    path('newslettermembership/create/', create_news_letter_membership, name="create_news_letter_membership"),
    path('emailnotification/create/<int:pk>/<int:membership>/', create_email_notification, name="create_email_notification"),
    path('emailtemplate/<int:pk>/', email_template, name="email_template"),
    path('reports/', reports, name="reports"),
    path('reports/<int:pk>/', show_report, name='report_detail'),
    path('reports/list/', list_report, name="report_list"),
    path('reports/<str:key>/', filters_extra, name="extra_filters"),
    path('reporttype/add', add_reporttype_view, name='add_reporttype'),
    path('reports/graph_download/', download_graph, name="download_graph"),

]
