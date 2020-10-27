from django.urls import path

from api.views import ReporteDeleteView

urlpatterns = [
    path('report/delete/', ReporteDeleteView.as_view(), name='api_report_delete'),
]