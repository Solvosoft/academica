from rest_framework import serializers
from rest_framework.utils.mediatypes import order_by_precedence

from matricula.models import Course, Group


class CourseSerializerForTable(serializers.ModelSerializer):
    enroll_count = serializers.IntegerField()

    class Meta:
        model = Course
        fields = ['name', 'enroll_count']



class CourseDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=CourseSerializerForTable(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)


class ApprovedCourseSerializerForTable(serializers.ModelSerializer):
    approved_count = serializers.IntegerField()

    class Meta:
        model = Course
        fields = ['name', 'approved_count']


class ApprovedCourseDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=ApprovedCourseSerializerForTable(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)

class CourseTopicsSerializerForTable(serializers.Serializer):
    course_id__name = serializers.CharField()
    enroll_finish__year = serializers.IntegerField()
    enroll_finish__month = serializers.IntegerField()
    course_id__category_id__name = serializers.CharField()


class CourseTopicsDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=CourseTopicsSerializerForTable(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)

