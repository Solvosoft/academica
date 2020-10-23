from django.urls import path

from membership_manager.reports import view as reports_view
from membership_manager import views as base_views
from . import activityreportview
from . import contacts_view
from . import invoice_view
from . import memberships_view
from . import news_letter_view
from . import organizations_view
from . import user_view
from . import templates_view


urlpatterns = [
    path('home/', base_views.index, name="home"),
    path('contacts/', contacts_view.ContactListView.as_view(), name="contacts"),
    path('contacts/create', contacts_view.create_contacts, name="create_contacts"),
    path('contacts/edit/<int:pk>', contacts_view.EditContact.as_view(), name="edit_contacts"),
    path('contacts/delete/<int:pk>/', contacts_view.delete_contacts, name="delete_contacts"),
    path('contacts/deactivate/<int:pk>/', contacts_view.deactivate_contact, name="deactivate_contact"),
    path('organizations/', organizations_view.OrganizationListView.as_view(), name="organizations"),
    path('organizations/create', organizations_view.create_organization, name="create_organizations"),
    path('organizations/edit/<int:pk>', organizations_view.EditOrganization.as_view(), name="edit_organizations"),
    path('organizations/delete/<int:pk>/', organizations_view.delete_organization, name="delete_organizations"),
    path('organizations/deactivate/<int:pk>/', organizations_view.deactivate_organization, name="deactivate_organization"),
    path('memberships/', memberships_view.MembershipListView.as_view(), name="memberships"),
    path('memberships/create', memberships_view.create_membership, name="create_memberships"),
    path('memberships/edit/<int:pk>', memberships_view.EditMembership.as_view(), name="edit_memberships"),
    path('memberships/delete/<int:pk>/', memberships_view.delete_memberships, name="delete_memberships"),
    path('memberships/deactivate/<int:pk>/', memberships_view.deactivate_membership, name="deactivate_membership"),
    path('newsletter/', news_letter_view.news_letter_list, name="news_letter_list"),
    path('services/', base_views.services_list, name="services_list"),
    path('services/edit/<int:pk>', base_views.EditService.as_view(), name="edit_service"),
    path('newsletter/create/<int:pk>/', news_letter_view.create_news_letter, name="create_news_letter"),
    path('newsletter/send/<int:pk>/', news_letter_view.send_news_letter, name="send_news_letter"),
    path('newsletter/delete/<int:pk>/', news_letter_view.delete_news_letter, name="delete_news_letter"),
    path('services/delete/<int:pk>/', base_views.delete_service, name="delete_service"),
    path('newsletter/update_emails/<int:pk>/', news_letter_view.update_emails_news_letter, name="update_emails_news_letter"),
    path('newsletter/edit/<int:pk>/', news_letter_view.EditNewsLetter.as_view(), name="edit_news_letter"),
    path('task/create/<int:pk>/', news_letter_view.create_task, name="create_task"),
    path('task/delete/<int:pk>/', news_letter_view.delete_task, name="delete_task"),
    path('newslettertemplate/create/', news_letter_view.create_news_letter_template, name="create_news_letter_template"),
    path('newslettermembership/create/', news_letter_view.create_news_letter_membership, name="create_news_letter_membership"),
    path('emailnotification/create/<int:pk>/<int:membership>/', base_views.create_email_notification, name="create_email_notification"),
    path('emailtemplate/<int:pk>/', base_views.email_template, name="email_template"),
    path('reports/', reports_view.reports, name="reports"),
    path('reports/<int:pk>/', reports_view.show_report, name='report_detail'),
    path('reports/list/', reports_view.list_report, name="report_list"),
    path('reports/graph_download/', reports_view.download_graph, name="download_graph"),
    path('reports/<str:key>/', reports_view.filters_extra, name="extra_filters"),
    path('reporttype/add', reports_view.add_reporttype_view, name='add_reporttype'),
    path('invoice/actions', invoice_view.invoiceAction, name='invoice-actions'),
    path('invoice/list', invoice_view.InvoiceListView.as_view(), name='invoice-list'),
    path('invoice/<int:pk>/', invoice_view.InvoiceChangeView.as_view(), name='invoice-edit'),
    path('invoice/pay/<int:pk>/', invoice_view.InvoicePayView.as_view(), name='invoice-pay'),
    path('activityReport/add', activityreportview.ActivityReportAdd.as_view(), name="activityreport-add"),
    path('activityReport/<int:pk>/', activityreportview.ActivityReportEdit.as_view(), name="activityreport-edit"),
    path('activityReport/', activityreportview.ActivityReportList.as_view(), name="activityreport-list"),
    path('activityReport_addhour/', activityreportview.addHour, name="activityreporthour-add"),
    path('users/list/', user_view.UserListView.as_view(), name="user_list"),
    path('users/create', user_view.AddUser.as_view(), name="create_user"),
    path('users/edit/<int:pk>', user_view.EditUser.as_view(), name="edit_user"),
    path('users/delete/<int:pk>/', user_view.delete_user, name="delete_user"),
    path('users/deactivate/<int:pk>/', user_view.deactivate_user, name="deactivate_user"),
    path('groups/', user_view.groups_list, name="groups_list"),
    path('groups/edit/<int:pk>', user_view.EditGroup.as_view(), name="edit_group"),
    path('groups/delete/<int:pk>/', user_view.delete_group, name="delete_group"),
    path('templates/', templates_view.TemplateListView.as_view(), name="templates"),
    path('templates/create', templates_view.create_template, name="create_template"),
    path('templates/edit/<int:pk>', templates_view.EditTemplate.as_view(), name="edit_template"),
    path('templates/delete/<int:pk>/', templates_view.delete_template, name="delete_template"),
    path('logentry/list/<str:model>/', base_views.logentry_list, name="logentry_list"),
    path('logentry/', base_views.logentry_filter_view, name="logentry_filter"),
    path('logentry/<str:app>/<str:model>/<int:pk>', base_views.logentry_object, name="logentry_object"),

]
