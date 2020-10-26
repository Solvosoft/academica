from datetime import datetime

from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from membership_manager.models import Report
from django.http import Http404

from membership_manager.utils import add_logentry


class ReporteDeleteView(APIView):

    def delete(self, request):

        if request.user.has_perm('membership_manager.delete_report'):

            if 'pk' in request.data:
                report = Report.objects.filter(pk=request.data['pk']).first()
                object_repr = str(report)
                object_pk = report.pk
                report.delete()
                add_logentry("membership_manager", "report", object_pk, object_repr, request.user, 3)
            return Response({'result': True}, status=status.HTTP_201_CREATED)

        else:
            raise Http404("No tiene los permisos suficientes para realizar esta acción.")