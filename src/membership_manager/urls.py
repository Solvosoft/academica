from django.urls import path
from membership_manager import views
from membership_manager.news_letter import create_news_letter,\
        news_letter_list, send_news_letter, delete_news_letter
from membership_manager.views import OrganizationView,\
        MembershipListView, ContactListView, create_membership
from django.contrib.auth.decorators import login_required

organization_view = OrganizationView()
urlpatterns = [
    path('home/', views.index, name="home"),
    path(
        'contacts/',
        login_required(ContactListView.as_view()), name="contacts"),
    path(
        'organizations/',
        login_required(MembershipListView.as_view()), name="organizations"),
    path('memberships/', MembershipListView.as_view(), name="memberships"),
    path('memberships/create', create_membership, name="create_memberships"),
    path('newsletter/', news_letter_list, name="news_letter_list"),
    path(
        'newsletter/create/<int:pk>/',
        create_news_letter, name="create_news_letter"),
    path(
        'newsletter/send/<int:pk>/',
        send_news_letter, name="send_news_letter"),
    path(
        'newsletter/delete/<int:pk>/',
        delete_news_letter, name="delete_news_letter"),
]
