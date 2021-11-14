from rest_framework import serializers
from rest_framework.utils.mediatypes import order_by_precedence

from matricula.models import Course, Group
from matricula.utils import get_label_months


class CourseSerializerForTable(serializers.ModelSerializer):
    enroll_count = serializers.IntegerField()

    class Meta:
        model = Course
        fields = ['name', 'enroll_count', 'workload']



class CourseDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=CourseSerializerForTable(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)


class ApprovedCourseSerializerForTable(serializers.ModelSerializer):
    approved_count = serializers.IntegerField()

    class Meta:
        model = Course
        fields = ['name', 'approved_count', 'workload']


class ApprovedCourseDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=ApprovedCourseSerializerForTable(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)

class CourseTopicsSerializerForTable(serializers.Serializer):
    course_id__name = serializers.CharField()
    enroll_finish__year = serializers.IntegerField()
    enroll_finish__month = serializers.SerializerMethodField()
    course_id__category_id__name = serializers.CharField()
    course_id__workload = serializers.CharField()

    def get_enroll_finish__month(self, obj):
        if obj is not None:
            return get_label_months(obj['enroll_finish__month'])
        return ""


class CourseTopicsDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=CourseTopicsSerializerForTable(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)

class OrganizationDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=CourseTopicsSerializerForTable(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)
