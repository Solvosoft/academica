from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Q
from django.shortcuts import render
from django_filters.rest_framework import FilterSet, DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from matricula.models import Course, Group, Enroll
from matricula.serializers import CourseTopicsDataTableSerializer


@permission_required('matricula.view_reports')
def course_topics_report(request):
    return render(request, 'reports/course_topics_report.html')


def get_queryset():
    return Group.objects.filter(enroll__enroll_finished=True).values(
        'course_id__name', 'enroll_finish__year', 'enroll_finish__month', 'course_id__category_id__name'
    ).order_by('course_id__name')


class CourseTopicsFilterSet(FilterSet):
    filter_fields = {'course_id__name': ['icontains']}


class CourseTopicsViewSet(viewsets.ModelViewSet):
    queryset = get_queryset()
    serializer_class = CourseTopicsDataTableSerializer
    filter_class = CourseTopicsFilterSet
    ordering_fields = ['enroll_finish__year', 'enroll_finish__month']
    ordering = ['-enroll_finish__year', '-enroll_finish__month']
    search_fields = ['course_id__name']
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset)
        response = {
            'data': queryset,
            'draw': self.request.GET.get('draw', 1),
            'recordsTotal': self.queryset.distinct().count(),
            'recordsFiltered': queryset.distinct().count()
        }
        return Response(self.get_serializer(response).data)
