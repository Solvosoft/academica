from django.urls import path
from membership_core.views import index

urlpatterns = [
   path('', index)
]