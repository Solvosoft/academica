from django.urls import path
from membership_manager import views
from membership_manager.news_letter import news_letter, create_news_letter
from membership_manager.views import ContactView, OrganizationView, MembershipListView


contact_view = ContactView()
organization_view = OrganizationView()
urlpatterns = [
    path('home/', views.index, name="home"),
    path('contacts/', MembershipListView.as_view(), name="contacts"),
    path('organizations/', MembershipListView.as_view(), name="organizations"),
    path('memberships/', MembershipListView.as_view(), name="memberships"),
    path('newsletter/', news_letter, name="news_letter"),
    path('newsletter/create/<int:pk>/', create_news_letter, name="create_news_letter"),
]
