# encoding: utf-8
'''
Created on 16/5/2015

@author: luisza
'''
from django.contrib.auth.decorators import login_required
from .utils import get_active_period
from django.shortcuts import render, get_object_or_404
from matricula.models import Course, Category, Group


def list_courses(request):

    cat = request.GET.get('cat', '')
    period = get_active_period()

    category = Category.objects.filter(course__group__period=period).distinct()
    if cat:
        category = category.filter(pk=cat)
    if len(category) > 1:
        return render(request, 'categories.html', {'categories': category})

    # courses = Course.objects.filter(category=category, group__period=period).distinct()
    groups = Group.objects.filter(period=period, course__category=category).order_by('course')
    courses = {}
    for group in groups:
        course = group.course
        if course.pk not in courses:
            courses[course.pk] = {'course': course,
                                  'groups': []}
        courses[course.pk]['groups'].append(group)

    return render(request, 'courses.html', {'courses': courses})


def view_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    period = get_active_period()
    groups = Group.objects.filter(period=period, course=course)

    return render(request, 'course.html',
                        {'course': {'course':course, 'groups': groups},
                        'add_schedule':True})
