'''
Created on 16/5/2015

@author: luisza
'''
from django.contrib.auth.decorators import login_required
from .utils import get_active_period
from django.shortcuts import render, get_object_or_404
from matricula.models import Course, Category


def list_courses(request):

    cat = request.GET.get('cat', '')
    period = get_active_period()
    category = Category.objects.filter(course__group__period=period).distinct()
    if cat:
        category = category.filter(pk=cat)
    if len(category) > 1:
        return render(request, 'categories.html', {'categories': category})

    courses = Course.objects.filter(category=category, group__period=period).distinct()
    return render(request, 'courses.html', {'courses': courses})


def view_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'course.html',
                        {'course': course,
                        'add_schedule':True})   