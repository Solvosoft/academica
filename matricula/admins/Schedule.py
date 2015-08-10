from matricula.models import Week, Hour
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from matricula.views.utils import get_active_period


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
        s = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
        hours_name = ["Day"]

        hours_name += [ "%.2d:00 AM" % (x) for x in range(12)] + ["12:00 MD"]
        hours_name += [ "%.2d:00 PM" % (x) for x in range(1, 12)]        

        pos = 0
        day = 0
        week = [hours_name]
        for x in range(7):
            l = [y for y in range(x * 24, x * 24 + 24)]
            l.insert(0, s[x])
            week.append(l)


        dev = '<input type="hidden" name="%s"  value="%s" class="week_input">' % (name, value)
        dev += '<table id="%s" name="%s" class="hour_table">' % (name, name)

        for pos, base in list(enumerate(week[0])):
            dev += "<tr><th>" + base + '</th>'
            td_class = ""
            if pos % 6 == 0:
                td_class = "six"
            for x in range(7):
                dev += '<th class="%s">' % (td_class) if not pos else '<td class="hour %s">' % (td_class)
                d = week[x + 1][pos]  if not pos else ""
                dev += '<span id="%s" class="%s"> %s</span>' % (str(week[x + 1][pos]), "", d)
                dev += "</th>" if not pos else "</td>"
            dev += "</tr>"
        dev += "</table>"

        return mark_safe(dev)




    week.short_description = _("Week")

    class Media:
        css = {
               'all': ('css/weekforms.css',),
               }
        js = ('django_ajax/js/jquery.ajax.min.js',
              'django_ajax/js/jquery.ajax-plugin.min.js',
              'js/weekforms.js')
