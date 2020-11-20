# encoding: utf-8
'''
Created on 16/5/2015

@author: luisza
'''
from .utils import get_active_period
from django.shortcuts import render, get_object_or_404
from matricula.models import Course, Category, Group, Professor
from matricula.forms import CourseMainSearchForm


def list_courses(request):
    form_search = CourseMainSearchForm()
    cat = request.GET.get('cat', None)
    period = get_active_period()
    show_info_modal = 0
    if request.user.is_authenticated:
        professor = Professor.objects.filter(user=request.user).first()
        if professor:
            if professor.email:
                if professor.email == "":
                    show_info_modal = 1
            else:
                show_info_modal = 1

            if professor.description:
                if professor.description == "":
                    show_info_modal = 1
            else:
                show_info_modal = 1

    category = Category.objects.filter(course__group__period=period).distinct()
    if cat:
        category = category.filter(pk=cat)
    if len(category) > 1:
        return render(request, 'categories.html', {
            'categories': category, 'form_search': form_search})

    # courses = Course.objects.filter(
    #   category=category, group__period=period).distinct()
    groups = Group.objects.filter(
        period=period, course__category__in=category.all()).order_by('course')
    courses = {}
    for group in groups:
        course = group.course
        if course.pk not in courses:
            courses[course.pk] = {'course': course,
                                  'groups': []}
        courses[course.pk]['groups'].append(group)
    return render(request, 'courses.html', {
        'courses': courses, 'show_info_modal': show_info_modal,
        'form_search': form_search})


def view_course(request, pk=None):
    period = get_active_period()
    form_search = CourseMainSearchForm(request.GET)
    form_search.is_valid()
    if pk is not None:
        course = get_object_or_404(Course, pk=pk)
        groups = Group.objects.filter(period=period, course=course)
    else:
        course = Course.objects.all()
        groups = Group.objects.filter(period=period)
        if form_search.cleaned_data['category']:
            course = course.filter(
                category__in=form_search.cleaned_data['category'])
            groups = Group.objects.filter(period=period, course__in=course)
        if int(form_search.cleaned_data['is_paid']) == 1:
            groups = groups.filter(is_paid=True)
        elif int(form_search.cleaned_data['is_paid']) == 2:
            groups = groups.filter(is_paid=False)
    return render(request, 'course.html', {
            'course': {'course': course, 'groups': groups},
            'add_schedule': True, 'form_search': form_search
        }
    )
