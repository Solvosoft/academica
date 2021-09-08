from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response

from matricula.models import Course
from matricula.serializers import CourseDataTableSerializer, CourseSerializerForTable


@permission_required('matricula.view_reports')
def ranking_course_enrolls_view(request):
    context = {}
    return render(request, 'reports/ranking_course_enrolls.html', context=context)

class RankingCourseEnrollsViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseDataTableSerializer
    ordering_fields = ['enroll_count']
    ordering = ['-enroll_count']

    def get_queryset(self):
        #Hacer annotate para realizar un count de enroll_count
        return Course.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        response = {
            'data': queryset,
            'draw': self.request.GET.get('draw', 1),
            'recordsTotal': self.queryset.distinct().count(),
            'recordsFiltered': queryset.distinct().count()
        }
        return Response(self.get_serializer(response).data)


