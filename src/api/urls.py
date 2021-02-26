from django.urls import path
from membership_manager.views import index

urlpatterns = [
   path('', index)
]