from django.urls import path
from membership_manager import views
urlpatterns = [
    path('template/contact/create', views.create_membership_contact_by_template,
         name="create_membership_contact_by_template")
]