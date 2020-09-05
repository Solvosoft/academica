from django.urls import path, include
from membership_manager import views
from membership_manager.views import ContactView, OrganizationView


contact_view = ContactView()
organization_view = OrganizationView()
urlpatterns = [
    path('home/', views.index, name="home"),
    path('', include(contact_view.get_urls())),
    path('', include(organization_view.get_urls()))
]
