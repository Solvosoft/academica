from async_notifications.models import NewsLetterTask
from rest_framework import serializers


class NewsLetterTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsLetterTask
        fields = ('send_date', )

class NewsLetterTaskListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_tipo_name')

    def get_tipo_name(self, obj):
        return obj.list_name


    class Meta:
        model = NewsLetterTask
        fields = ['id', 'name']