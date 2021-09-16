from django.contrib.auth.decorators import permission_required
from django.db.models import Count, Q
from django.shortcuts import render
from django_filters.rest_framework import FilterSet, DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication,BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from matricula.models import Course
from matricula.serializers import ApprovedCourseDataTableSerializer


@permission_required('matricula.view_reports')
def ranking_course_approved_view(request):
    context = {}
    return render(request, 'reports/ranking_course_approved.html', context=context)


class ApprovedRankingFilterSet(FilterSet):
    class Meta:
        model = Course
        fields = {'name': ['icontains']}


class RankingCourseApprovedViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().annotate(
            approved_count=Count('group__enroll', filter=Q(
                group__enroll__enroll_finished=True, group__enroll__course_status='approved'))).\
            values('name','approved_count').order_by('-approved_count')
    serializer_class = ApprovedCourseDataTableSerializer
    filter_class = ApprovedRankingFilterSet
    search_fields = ['name']
    ordering_fields = ['approved_count']
    ordering = ['-approved_count']
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    #intento de verificar autenticacion en la API
    #authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.queryset)
        response = {
            'data': queryset,
            'draw': self.request.GET.get('draw', 1),
            'recordsTotal': self.queryset.distinct().count(),
            'recordsFiltered': queryset.distinct().count()
        }
        return Response(self.get_serializer(response).data)
