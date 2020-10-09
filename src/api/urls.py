from django.urls import path

from api.organization import OrganizationView
from api.views import ReporteDeleteView

urlpatterns = [
    path('report/delete/', ReporteDeleteView.as_view(), name='api_report_delete'),
    path('organization/<int:pk>/', OrganizationView.as_view(), name='api_organization'),
]