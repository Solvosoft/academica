from django.db.models import Q
from rest_framework import serializers

from matricula.models import Course, Group
from matricula.utils import get_label_months


class CourseSerializerForTable(serializers.ModelSerializer):
    enroll_count = serializers.IntegerField()
    has_groups = serializers.SerializerMethodField()

    def get_has_groups(self, obj):
        return True if obj.group_set.all() else False

    class Meta:
        model = Course
        fields = ['id', 'name', 'enroll_count', 'workload', 'has_groups']



class CourseDataTableSerializer(serializers.Serializer):
    data = serializers.ListField(child=CourseSerializerForTable(), required=True)
    draw = serializers.IntegerField(required=True)
    recordsFiltered = serializers.IntegerField(required=True)
    recordsTotal = serializers.IntegerField(required=True)


class ApprovedCourseSerializerForTable(serializers.ModelSerializer):
    approved_count = serializers.IntegerField()
    has_groups = serializers.SerializerMethodField()

    def get_has_groups(self, obj):
        return True if obj.group_set.all() else False

    class Meta:
        model = Course
        fields = ['id', 'name', 'approved_count', 'workload', 'has_groups']


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


class GroupSerializer(serializers.ModelSerializer):
    enroll_count = serializers.SerializerMethodField()
    course_approved_count = serializers.SerializerMethodField()

    def get_enroll_count(self, obj):
        return obj.enroll_set.all().count()

    def get_course_approved_count(self, obj):
        filter = Q(enroll_finished=True, course_status='approved')
        return obj.enroll_set.all().filter(filter).count()

    class Meta:
        model = Group
        fields = ['name', 'enroll_count', 'course_approved_count', 'duration_hours']