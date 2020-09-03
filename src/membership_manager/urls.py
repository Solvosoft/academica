from django.urls import path
from membership_manager import views


urlpatterns = [
    path('home/', views.index, name="home")
]
