from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from membership_manager.models import Report
from django.http import Http404

class ReporteDeleteView(APIView):

    def delete(self, request):

        if request.user.has_perm('membership_manager.delete_report'):

            if 'pk' in request.data:
                Report.objects.filter(pk=request.data['pk']).delete()
            return Response({'result': True}, status=status.HTTP_201_CREATED)

        else:
            raise Http404("No tiene los permisos suficientes para realizar esta acción.")