from django.urls import path
from membership_manager import views
from membership_manager.news_letter import create_news_letter, news_letter_list, send_news_letter, delete_news_letter, \
    EditNewsLetter, create_task, delete_task, create_news_letter_template
from membership_manager.views import OrganizationView, MembershipListView, \
    ContactListView, create_membership, add_services, delete_membership_service, create_news_letter_membership, \
    create_email_notification, email_template

from django.contrib.auth.decorators import login_required

organization_view = OrganizationView()
urlpatterns = [
    path('home/', views.index, name="home"),
    path('contacts/', login_required(ContactListView.as_view()), name="contacts"),
    path('organizations/', login_required(MembershipListView.as_view()), name="organizations"),
    path('memberships/', MembershipListView.as_view(), name="memberships"),
    path(
        'membership/add_services/<int:pk>/',
        add_services, name="add_membership_services"),
    path(
        'membership/delete_service/<int:pk>/', delete_membership_service,
        name="delete_membership_service"),
    path('memberships/create', create_membership, name="create_memberships"),
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
]
