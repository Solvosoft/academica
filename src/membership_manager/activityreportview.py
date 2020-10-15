from django.contrib.auth.decorators import permission_required
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views.generic import ListView, CreateView, UpdateView
from membership_manager.forms import ActivityReportForm, ActivityReportAddForm, ActivityReportHours
from membership_manager.models import ActivityReport
import datetime


def parse_date(text):
      #15/10/2020
    return datetime.datetime.strptime(text, "%d/%m/%Y").date()


@method_decorator(permission_required('membership_manager.view_activityreport'), name='dispatch')
class ActivityReportList(ListView):
    model = ActivityReport
    ordering = ['-start_date']
    paginate_by = 50

    def get_dates(self, text):
        date = text.split('-')
        return [parse_date(date[0].strip()), parse_date(date[1].strip())]

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = ActivityReportForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['organization']:
            queryset = queryset.filter(organization__in=self.form.cleaned_data['organization'])
        if self.form.cleaned_data['daterange']:
            dates = self.get_dates(self.form.cleaned_data['daterange'])
            queryset = queryset.filter(
                start_date__gte=dates[0],
                end_date__lte=dates[1]
            )
        return queryset

    def get_getparams(self):
        dev = []
        for key in self.form.cleaned_data:
            if self.form.cleaned_data[key]:
                if isinstance(self.form.cleaned_data[key], QuerySet):
                    dev+=[(key, str(id)) for id in self.form.cleaned_data[key].values_list('pk', flat=True)]
                else:
                    dev.append((
                      key, self.form.cleaned_data[key]
                    ))
        if dev:
            dev = '?'+urlencode(dev)+'&'
        else:
            dev = '?'
        return dev

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['getparams'] = self.get_getparams()
        context['filterform'] = self.form
        context['hoursform'] = ActivityReportHours()
        return context


@method_decorator(permission_required('membership_manager.view_activityreport'), name='dispatch')
class ActivityReportAdd(CreateView):
    model = ActivityReport
    form_class = ActivityReportAddForm
    success_url = reverse_lazy('activityreport-list')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

@method_decorator(permission_required('membership_manager.change_activityreport'), name='dispatch')
class ActivityReportEdit(UpdateView):
    model = ActivityReport
    form_class = ActivityReportAddForm
    success_url = reverse_lazy('activityreport-list')

@permission_required('membership_manager.change_activityreport')
def addHour(request):
    return JsonResponse({'result': 'ok'})