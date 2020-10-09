from django.urls import path

from membership_manager.reports.view import reports, add_reporttype_view, download_graph, show_report, list_report, \
    filters_extra
from membership_manager.views import create_email_notification, email_template, index
from membership_manager.views import delete_membership_service
from .contacts_view import ContactListView, create_contacts, delete_contacts, EditContact
from .memberships_view import MembershipListView, create_membership, delete_memberships, EditMembership
from .news_letter_view import news_letter_list, create_news_letter, send_news_letter, delete_news_letter, \
    EditNewsLetter, \
    delete_task, create_news_letter_template, create_task, create_news_letter_membership
from .organizations_view import OrganizationListView, create_organization, delete_organization, \
    EditOrganization

urlpatterns = [
    path('home/', index, name="home"),
    path('contacts/', ContactListView.as_view(), name="contacts"),
    path('contacts/create', create_contacts, name="create_contacts"),
    path('contacts/edit/<int:pk>', EditContact.as_view(), name="edit_contacts"),
    path('contacts/delete/<int:pk>/', delete_contacts, name="delete_contacts"),
    path('organizations/', OrganizationListView.as_view(), name="organizations"),
    path('organizations/create', create_organization, name="create_organizations"),
    path('organizations/edit/<int:pk>', EditOrganization.as_view(), name="edit_organizations"),
    path('organizations/delete/<int:pk>/', delete_organization, name="delete_organizations"),
    path('memberships/', MembershipListView.as_view(), name="memberships"),
    path(
        'membership/delete_service/<int:pk>/', delete_membership_service,
        name="delete_membership_service"),
    path('memberships/create', create_membership, name="create_memberships"),
    path('memberships/edit/<int:pk>', EditMembership.as_view(), name="edit_memberships"),
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
    path('reports/graph_download/', download_graph, name="download_graph"),
    path('reports/<str:key>/', filters_extra, name="extra_filters"),
    path('reporttype/add', add_reporttype_view, name='add_reporttype'),


]
