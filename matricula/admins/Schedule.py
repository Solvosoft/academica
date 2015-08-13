from matricula.models import Week, Hour, ClassroomSchedule, \
    ClassroomGroupProfesor, ProfesorSchedule, Group, Period
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from matricula.views.utils import get_active_period
from django.template.loader import render_to_string
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.http import JsonResponse


class ScheduleAdmin(object):
    scheduleModel = None
    schedule_filter = None
    same_model = False

    def get_filters_params(self, obj):
        args = {
                'period': get_active_period(),
                }
        if not self.schedule_filter:
            args[obj.__class__.__name__.lower()] = obj
        else:
            for name in self.schedule_filter:
                if hasattr(obj, name):
                    args[name] = getattr(obj, name)
        return args

    def week(self, obj=None):
        value = ""
        if obj and obj.pk:
            if self.same_model:
                schedule = [ obj ]
                if obj.schedule is None:
                    obj.schedule = Week.objects.create()
                    obj.save()
            else:
                args = self.get_filters_params(obj)
                schedule = self.scheduleModel.objects.filter(**args)
            if schedule:
                # FIXME check only one schedule
                schedule = schedule[0]
                hours = [str(x["day_position"]) for x in schedule.schedule.hours.filter(active=True).values("day_position")]
                value = ";".join(hours)

        return self.render_week("schedule", value, None)


    def save_model(self, request, obj, form, change):
        if change:
            if not self.same_model:
                args = self.get_filters_params(obj)
                # FIXME check if schedule exist
                schedule = self.scheduleModel.objects.filter(**args)
                if schedule:
                    schedule = schedule[0]
                else:
                    week = Week()
                    args = self.get_filters_params(obj)
                    args["week"] = week
    
                    schedule = self.scheduleModel.objects.create(**args)
                    obj.schedule = schedule
                    obj.save()
            else:
                schedule = obj
                if obj.schedule is None:
                    obj.schedule = Week.objects.create()

            schedule_hour = request.POST.getlist('schedule', [])
            if schedule_hour:
                schedule_hour = list(map(int, schedule_hour[0].split(";")))
                hours = schedule.schedule.hours.all()
                for hour in hours:
                    if hour.day_position in schedule_hour:
                        if not hour.active:
                            hour.active = True
                            hour.save()
                        del schedule_hour[schedule_hour.index(hour.day_position)]
                    else:
                        hour.active = False
                        hour.save()
                for hday in schedule_hour:
                    h = Hour.objects.create(day_position=hday, active=True)
                    schedule.schedule.hours.add(h)
            else:
                schedule.schedule.hours.all().update(active=False)

        else:  # in creation
            schedule = request.POST.getlist('schedule', [])
            week = Week.objects.create()
            if schedule:
                hours = schedule[0].split(";")
                for hour in hours:
                    h = Hour.objects.create(day_position=int(hour), active=True)
                    week.hours.add(h)
            if self.same_model:
                obj.schedule = week
            else:
                args = self.get_filters_params(obj)
                args["schedule"] = week
                obj.schedule = self.scheduleModel.objects.create(**args)
            obj.save()
        # obj.save()



    def render_week(self, name, value, attrs=None):
        dev = '<input type="hidden" name="%s"  value="%s" class="week_input">' % (name, value)
        dev += render_to_string("matricula/week.html", {'name': name})
        dev = dev.replace("\n", "")
        return mark_safe(dev)

    week.short_description = _("Week schedule")

    class Media:
        css = {
               'all': ('css/weekforms.css',),
               }
        js = ('js/weekforms.js',)


class GroupSchedule(ScheduleAdmin):

    def get_urls(self):
        my_urls = [
            url(r'^classroom_hours$', self.get_classroom_schedule,
                name="classroom_hours"),
            url(r'^profesor_hours$', self.get_profesor_schedule,
                name="profesor_hours"),
            url(r'^group_hours$', self.get_group_schedule,
                name="group_hours"),
        ]
        return my_urls

    def get_schedules(self, request, base_class, _type,):
        dev = {'selected': [],
               'type': _type,
               'hours': [] } 
        pk = request.GET.get('pk', 0)
        if pk:
            pk = int(pk)
        else:
            return JsonResponse(dev)
        period = get_active_period()
        args = {'period': period,
                _type + "__pk": pk,
               }


        cschedule = base_class.objects.filter(**args)
        if cschedule:
            cschedule = cschedule[0]
            dev['hours'] = [str(x["day_position"]) for x in cschedule.schedule.hours.filter(active=True).values("day_position")]
        args = {'period': period,
                _type: pk,
               }
        selected = ClassroomGroupProfesor.objects.filter(**args)
        if selected:
            for sel in selected:
                dev['selected'] = [str(x["day_position"]) for x in sel.schedule.hours.filter(active=True).values("day_position")]

        return JsonResponse(dev)

    def get_classroom_schedule(self, request):
        return self.get_schedules(request, ClassroomSchedule, "classroom")

    def get_profesor_schedule(self, request):
        return self.get_schedules(request, ProfesorSchedule, "profesor")

    def get_group_schedule(self, request):
        dev = {'selected': [],
               'type': "schedule",
               'hours': []}
        pk = request.GET.get('pk', 0)
        if pk:
            pk = int(pk)
        else:
            return JsonResponse(dev)

        group = Group.objects.filter(pk=pk)
        if group:
            group = group[0]
            dev['selected'] = [str(x["day_position"]) for x in group.schedule.hours.filter(active=True).values("day_position")]
        return JsonResponse(dev)

    def render_week(self, name, value, attrs=None):
        dev = '<input type="hidden" name="%s"  value="%s" class="week_input">' % (name, value)
        dev += render_to_string("matricula/groupweek.html", {'name': name})
        dev = dev.replace("\n", "")

        dev += "<script> classroom_schedule_url='" + reverse(self.namespace + ":classroom_hours") + "';"
        dev += "profesor_schedule_url='" + reverse(self.namespace + ":profesor_hours") + "';"
        dev += "group_schedule_url='" + reverse(self.namespace + ":group_hours") + "';"
        dev += "</script>"
        return mark_safe(dev)

    def change_group(self, obj):
        print(obj.schedule, obj.group.schedule)
        
        if obj.schedule != obj.group.schedule:
            for_del = obj.group.schedule
            obj.group.schedule = obj.schedule
            obj.group.save()
            for_del.hours.all().delete()
            for_del.delete()

    class Media:
        css = {
               'all': ('css/weekgroupforms.css',),
               }
        js = ('js/weekforms.js', 'js/weekgroup.js')
