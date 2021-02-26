from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from membership_manager.dashboard import TopStats
from matricula.models import Category, Student
from membership_core.models import Country


def servicios_stats():
    for category in Category.objects.all():
        yield (category.name, category.course_set.count())


def country_stats():
    for country in Country.objects.all().order_by('name'):
        total = Student.objects.filter(country=country).distinct().count()
        if total:
            yield (country.flag, country.name, total)


@login_required
def index(request):
    if request.user.has_perm('membership_manager.can_show_dashboard'):
        context = {'topstat': TopStats(),
                #'vencimientoanual_url': reverse('vencimientoanual-list'),
                #'pagoanual_url': reverse('pagoanual-list'),
                'countries': country_stats(),
                'servicios_stats': servicios_stats()
                }
        return render(request, 'membership/home.html', context=context)
    return redirect(reverse('courses'))
