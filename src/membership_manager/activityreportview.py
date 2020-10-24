from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views.generic import ListView, CreateView, UpdateView

from membership_manager.forms import ActivityReportForm, ActivityReportAddForm, ActivityReportHours
from membership_manager.models import ActivityReport, Attention
from membership_manager.utils import add_logentry


def parse_date(text):
      #15/10/2020
    return datetime.strptime(text, "%d/%m/%Y").date()


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
        self.object = form.save()
        self.object.user = self.request.user
        self.object.save()
        object_repr = str(self.object) if len(str(self.object)) < 200 else str(self.object)[0:196] + "..."
        add_logentry("membership_manager", "activityreport", self.object.pk, object_repr, self.request.user, 1)
        return HttpResponseRedirect(self.get_success_url())

@method_decorator(permission_required('membership_manager.change_activityreport'), name='dispatch')
class ActivityReportEdit(UpdateView):
    model = ActivityReport
    form_class = ActivityReportAddForm
    success_url = reverse_lazy('activityreport-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activityreport = context['object']
        context['activityreport'] = activityreport.pk
        return context

    def form_valid(self, form):
        activityreport = form.save()
        object_repr = str(activityreport) if len(str(activityreport)) < 200 else str(activityreport)[0:196] + "..."
        add_logentry("membership_manager", "activityreport", activityreport.pk, object_repr, self.request.user, 2)
        messages.success(self.request, "Reporte de atención actualizado con éxito")
        return HttpResponseRedirect(self.get_success_url())

@permission_required('membership_manager.change_activityreport')
def addHour(request):
    form = ActivityReportHours(request.POST)
    if form.is_valid():
        obj = get_object_or_404(ActivityReport, pk=form.cleaned_data['item'])
        att = Attention.objects.create(activity=obj,
            start_date=form.cleaned_data['start_date'],
            end_date=form.cleaned_data['end_date']
        )
        obj.manual_edited=False
        obj.save()
    return JsonResponse({'result': 'ok', 'item': form.cleaned_data['item'],
                         'duration': int(obj.duration), 'time': "%s a %s"%(
            att.start_date.strftime('%b %d, %Y %I:%M %p').lower(), att.end_date.strftime('%b %d, %Y %I:%M %p').lower())
                         })
