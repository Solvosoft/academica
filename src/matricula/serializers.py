from django.db.models import Count, Q
from rest_framework import serializers

from matricula.models import Course, Enroll


class CourseSerializerForTable(serializers.ModelSerializer):
    enroll_count = serializers.SerializerMethodField()

    def get_enroll_count(self, course):
        groups = course.group_set.all()
        enroll_count = 0
        for group in groups:
            enroll_count += Enroll.objects.filter(group_id=group).count()
        return enroll_count

    class Meta:
        model = Course
        #Content se debe eliminar
        fields = ['name', 'content', 'enroll_count']

class CourseDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=CourseSerializerForTable(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)