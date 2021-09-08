# encoding: utf-8
'''
Created on 16/5/2015

@author: luisza
'''

from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from matricula.models import Course, Category, Group, Professor
from matricula.forms import CourseMainSearchForm
from matricula.views.utils import get_active_period


def list_courses(request):
    form_search = CourseMainSearchForm()
    cat = request.GET.get('cat', None)
    if cat is not None:
        try:
            cat = int(cat)
        except ValueError:
            cat = None
    period = get_active_period()
    show_info_modal = False
    context = {}
    if request.user.is_authenticated:
        professor = Professor.objects.filter(user=request.user).first()
        if professor:
            context['professor'] = professor
            show_info_modal = professor.email is None or professor.email == "" or professor.description is None \
                    or professor.description == ""

    category = Category.objects.filter(course__group__period__in=period).distinct()
    if cat:
        category = category.filter(pk=cat)
    if len(category) > 1:
        return render(request, 'categories.html', {
            'categories': category, 'form_search': form_search})

    # courses = Course.objects.filter(
    #   category=category, group__period=period).distinct()
    groups = Group.objects.filter(
        period__in=period, course__category__in=category.all()).order_by('course')
    courses = {}
    for group in groups:
        course = group.course
        if course.pk not in courses:
            courses[course.pk] = {'course': course,
                                  'groups': []}
        courses[course.pk]['groups'].append(group)
    context.update({
        'courses': courses, 'show_info_modal': show_info_modal,
        'form_search': form_search})
    return render(request, 'courses.html', context )


def view_course(request, pk=None):
    period = get_active_period()
    form_search = CourseMainSearchForm(request.GET)
    form_search.is_valid()
    if pk is not None:
        course = get_object_or_404(Course, pk=pk)
        groups = Group.objects.filter(period__in=period, course=course, is_open=True).all()
        groups = sorted(groups, key=lambda t: t.in_preenrollment, reverse=True)
    else:
        course = Course.objects.none()
        groups = Group.objects.filter(period__in=period)
        if 'category' in form_search.cleaned_data and form_search.cleaned_data['category']:
            groups = groups.filter(
                course__category__pk__in=form_search.cleaned_data['category'])
        if 'course' in form_search.cleaned_data and  form_search.cleaned_data['course']:
            groups = groups.filter(
                course__pk__in=form_search.cleaned_data['course'])
        is_paid = form_search.cleaned_data.get('is_paid', None)
        if is_paid is not None:
            if is_paid == '1':
                groups = groups.filter(is_paid=True)
            elif is_paid == '2':
                groups = groups.filter(is_paid=False)

        if 'course_name' in form_search.cleaned_data and form_search.cleaned_data['course_name']:
            groups = groups.filter(
                Q(name__icontains=form_search.cleaned_data['course_name'])|
                Q(course__name__icontains=form_search.cleaned_data['course_name'])|
                Q(course__category__name__icontains=form_search.cleaned_data['course_name']))
        groups = groups.filter(is_open=True)
        groups = sorted(groups, key=lambda t: t.in_preenrollment, reverse=True)
    context =   {
        'course': {'course': course, 'groups': groups},
        'add_schedule': True, 'form_search': form_search
    }
    return render(request, 'course.html', context)


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    context =   {
        'course': course,
    }
    return render(request, "course_detail.html", context)