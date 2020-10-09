from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from api.serializers import OrganizationCreateSerializer, OrganizationListSerializer
from membership_manager.models import Organization


class OrganizationView(APIView):
    def post(self, request, pk, format=None):
        organization = get_object_or_404(Organization, pk=pk)
        serializer = OrganizationCreateSerializer(data=request.data)
        if serializer.is_valid() and request.data.get('organization'):
            organization.contacts.add(request.data.get('organization'))
            serializer = OrganizationListSerializer(organization.contacts.all(), many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'organization': ['Debe seleccionar un contacto.']}, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, format=None):
        organization = get_object_or_404(Organization, pk=pk)
        if 'delitems[]' in request.data:
            del_items = request.data.getlist('delitems[]', [])
        else:
            del_items = []
        contactos = Organization.objects.filter(pk__in=del_items)
        for i in contactos:
            organization.contacts.remove(i)
            i.delete()
        serializer = OrganizationListSerializer(organization.contacts.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)