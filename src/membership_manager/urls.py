from django.urls import path
from membership_manager import views
urlpatterns = [
    path('accounts/profile/', views.index, name="home")
]
