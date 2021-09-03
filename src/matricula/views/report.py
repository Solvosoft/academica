from django.contrib.auth.decorators import user_passes_test, permission_required
from django.db.models import Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView

from matricula.forms import GroupSearchStudentReportForm
from matricula.models import Group, Enroll

@permission_required('matricula.view_reports')
def list_reports(request):
    return render(request, 'reports/list_reports.html')

@permission_required('matricula.view_reports')
def enrolls_report(request):
    labels = []
    data = []

    queryset = Enroll.objects.order_by('-student')[:10]
    for students in queryset:
        labels.append(students.enroll_activate)
        data.append(students.student)
    return render(request, 'reports/enrolls_report.html', {
        'labels': labels,
        'data': data
    })


@method_decorator(user_passes_test(lambda x: x.has_perm('matricula.view_enroll')), name='dispatch')
class GroupEstudentStatusList(ListView):
    model = Group
    template_name = 'groups/list_student_status.html'
    paginate_by = 50
    search_form = GroupSearchStudentReportForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['form_search'] = self.search_form
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {}
        self.search_form = self.search_form(self.request.GET)
        self.search_form.is_valid()
        if self.search_form.cleaned_data['name']:
            queryset = queryset.filter(
                Q(name__icontains=self.search_form.cleaned_data['name']) |
                Q(course__name__icontains=self.search_form.cleaned_data['name']) |
                Q(course__category__name__icontains=self.search_form.cleaned_data['name']))
        if self.search_form.cleaned_data['course']:
            filters['course__in'] = self.search_form.cleaned_data['course']
        if self.search_form.cleaned_data['period']:
            filters['period__in'] = self.search_form.cleaned_data['period']
        if self.search_form.cleaned_data['category']:
            filters['course__category__in'] = self.search_form.cleaned_data['category']
        if self.search_form.cleaned_data['open'] and int(
                self.search_form.cleaned_data['open']) != GroupSearchStudentReportForm.DO_NOT_APPLY:
            if int(self.search_form.cleaned_data['open']) == GroupSearchStudentReportForm.OPEN:
                filters['is_open'] = True
            else:
                filters['is_open'] = False

        return queryset.filter(**filters)
