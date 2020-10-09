from rest_framework import serializers

from membership_manager.models import Organization, Membership


class OrganizationCreateSerializer(serializers.Serializer):

    class Meta:
        model = Membership
        fields = ['organization']


class OrganizationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['id', 'name']