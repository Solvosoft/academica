from django.db.models import Q, Count
from django_filters.rest_framework import FilterSet, DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from matricula.forms import CourseTableForm
from matricula.models import Course, Student
from matricula.models import Group
from matricula.serializers import ApprovedCourseDataTableSerializer, CountriesGroupDataTableSerializer
from matricula.serializers import CourseDataTableSerializer
from matricula.serializers import CourseTopicsDataTableSerializer
from membership_core.models import Country


class ReportPermission(DjangoModelPermissions):
    perms_map = {
        'GET': ['matricula.view_reports'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

class RankingCourseEnrollsViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Course.objects.all().annotate(enroll_count=Count('group__enroll'))
    serializer_class = CourseDataTableSerializer
    ordering_fields = ['enroll_count']
    ordering = ['-enroll_count']
    search_fields = ['name']
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ReportPermission]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        form = CourseTableForm(self.request.GET)
        form.set_course_map()
        if form.is_valid():
            queryset = form.filter_queryset(queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().distinct())
        paginator = self.paginate_queryset(queryset)
        response = {
            'data': paginator,
            'draw': self.request.GET.get('draw', 1),
            'recordsTotal': self.queryset.count(),
            'recordsFiltered': queryset.count()
        }
        return Response(self.get_serializer(response).data)


class ApprovedRankingFilterSet(FilterSet):
    class Meta:
        model = Course
        fields = {'name': ['icontains']}


class RankingCourseApprovedViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Course.objects.all().annotate(
            approved_count=Count('group__enroll', filter=Q(
                group__enroll__enroll_finished=True, group__enroll__course_status='approved'))).order_by('-approved_count')
    serializer_class = ApprovedCourseDataTableSerializer
    filter_class = ApprovedRankingFilterSet
    search_fields = ['name', 'workload']
    ordering_fields = ['approved_count', 'workload']
    ordering = ['-approved_count']
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ReportPermission]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        form = CourseTableForm(self.request.GET)
        form.set_course_map()
        if form.is_valid():
            queryset = form.filter_queryset(queryset)
        return queryset

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset().distinct())
        paginator = self.paginate_queryset(queryset)
        response = {
            'data': paginator,
            'draw': self.request.GET.get('draw', 1),
            'recordsTotal': self.queryset.distinct().count(),
            'recordsFiltered': queryset.count()
        }
        return Response(self.get_serializer(response).data)



class CourseTopicsFilterSet(FilterSet):
    filter_fields = {'course_id__name': ['icontains']}


class CourseTopicsViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Group.objects.filter(enroll__enroll_finished=True).distinct()
    serializer_class = CourseTopicsDataTableSerializer
    filter_class = CourseTopicsFilterSet
    ordering_fields = ['enroll_finish__year', 'enroll_finish__month']
    ordering = ['course_id__name']
    search_fields = ['course_id__name']
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ReportPermission]

    def get_queryset(self):
        queryset=super().get_queryset()
        return queryset.values(
            'course_id__name', 'enroll_finish__year', 'enroll_finish__month', 'course_id__category_id__name',
            'course_id__workload'
        )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        form = CourseTableForm(self.request.GET)
        if form.is_valid():
            queryset = form.filter_queryset(queryset)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginator = self.paginate_queryset(queryset)
        response = {
            'data': paginator,
            'draw': self.request.GET.get('draw', 1),
            'recordsTotal': self.queryset.distinct().count(),
            'recordsFiltered': queryset.distinct().count()
        }
        return Response(self.get_serializer(response).data)


class CountriesGroupFilterSet(FilterSet):
    class Meta:
        model = Country
        fields = {'name': ['icontains']}


class CountriesGroupViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Country.objects.all()
    serializer_class = CountriesGroupDataTableSerializer
    filter_class = CountriesGroupFilterSet
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code']
    ordering = ['name']
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated, ReportPermission]

    def filter_queryset(self, queryset):
        pk = self.request.GET.get('pk', None)
        if pk:
            queryset = queryset.filter(student__enroll__group=pk).annotate(student_count=Count('student')).order_by('name')
            queryset = super().filter_queryset(queryset)
            return queryset
        return queryset.none()

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset().distinct())
        paginator = self.paginate_queryset(queryset)
        response = {
            'data': paginator,
            'draw': self.request.GET.get('draw', 1),
            'recordsTotal': self.queryset.distinct().count(),
            'recordsFiltered': queryset.count()
        }
        return Response(self.get_serializer(response).data)