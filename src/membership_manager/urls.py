from django.urls import path, include
from membership_manager import views
from membership_manager.views import ContactView

contact_view = ContactView()
urlpatterns = [
    path('home/', views.index, name="home"),
    path('', include(contact_view.get_urls()))
]
