# encoding: utf-8
'''
Created on 16/5/2015

@author: luisza
'''

from django.contrib import auth
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.urls import reverse

from async_notifications.utils import send_email_from_template

from matricula.models import Course, Category, Group, Professor, Student
from matricula.forms import CourseMainSearchForm, LoginForm, StudentCreateForm
from matricula.views.utils import get_active_period, get_expire_date


def list_courses(request):
    form_search = CourseMainSearchForm()
    cat = request.GET.get('cat', None)
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
        if form_search.cleaned_data['category']:
            groups = groups.filter(
                course__category__pk__in=form_search.cleaned_data['category'])
        if form_search.cleaned_data['course']:
            groups = groups.filter(
                course__pk__in=form_search.cleaned_data['course'])
        if form_search.cleaned_data['is_paid'] and int(form_search.cleaned_data['is_paid']) == 1:
            groups = groups.filter(is_paid=True)
        elif form_search.cleaned_data['is_paid'] and int(form_search.cleaned_data['is_paid']) == 2:
            groups = groups.filter(is_paid=False)
        if form_search.cleaned_data['name']:
            groups = groups.filter(
                Q(name__icontains=form_search.cleaned_data['name'])|
                Q(course__name__icontains=form_search.cleaned_data['name'])|
                Q(course__category__name__icontains=form_search.cleaned_data['name']))
        groups = groups.filter(is_open=True)
        groups = sorted(groups, key=lambda t: t.in_preenrollment, reverse=True)
    context =   {
        'course': {'course': course, 'groups': groups},
        'add_schedule': True, 'form_search': form_search,
        'display_form': '1', 'login_form': LoginForm(),
        'student_form': StudentCreateForm(), 'show_modal': "off",
    }
    if request.method == "POST":
        if request.POST.get('login-form', False):
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = auth.authenticate(
                    username=login_form.cleaned_data['username'],
                    password=login_form.cleaned_data['password2'])
                if user is not None and user.is_active:
                    auth.login(request, user)
                    context['authenticated'] = 'on'
                else:
                    context['login_errors'] = "on"
                    context['show_modal'] = 'on'
            else:
                context['login_form'] = login_form
                context['show_modal'] = 'on'
        else:
            student_form = StudentCreateForm(request.POST)
            if student_form.is_valid():
                user = User.objects.create_user(
                    student_form.cleaned_data['name'],
                    student_form.cleaned_data['email'],
                    student_form.cleaned_data['password'])
                user.first_name = student_form.cleaned_data['first_name']
                user.last_name = student_form.cleaned_data['last_name']
                user.is_active = False
                user.save()
                student = Student(
                    user=user, organization=student_form.cleaned_data['organization'],
                    country=student_form.cleaned_data['country'],
                    phone_number=student_form.cleaned_data['phone_number'],
                    expired_at=get_expire_date(),
                )
                student.save()
                schema = request.scheme+"://"
                send_email_from_template(
                    'new_user_created_academy', user.email,
                    {
                        "url": request.build_absolute_uri(reverse('confirm_email')),
                        'domain': schema+request.get_host(),
                        "user": user,
                        'student': student
                    },
                    enqueued=True,
                    user=None)
                context['display_form'] = '1'
                context['student_created'] = "on"
                context['show_modal'] = 'on'
            else:
                context['student_form'] = student_form
                context['display_form'] = '2'
                context['show_modal'] = 'on'
    return render(request, 'course.html', context)


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    context =   {
        'display_form': '1', 'login_form': LoginForm(),
        'student_form': StudentCreateForm(), 'show_modal': "off",
        'course': course,
    }
    if request.method == "POST":
        if request.POST.get('login-form', False):
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                user = auth.authenticate(
                    username=login_form.cleaned_data['username'],
                    password=login_form.cleaned_data['password2'])
                if user is not None and user.is_active:
                    auth.login(request, user)
                    context['authenticated'] = 'on'
                else:
                    context['login_errors'] = "on"
                    context['show_modal'] = 'on'
            else:
                context['login_form'] = login_form
                context['show_modal'] = 'on'
        else:
            student_form = StudentCreateForm(request.POST)
            if student_form.is_valid():
                user = User.objects.create_user(
                    student_form.cleaned_data['name'],
                    student_form.cleaned_data['email'],
                    student_form.cleaned_data['password'])
                user.first_name = student_form.cleaned_data['first_name']
                user.last_name = student_form.cleaned_data['last_name']
                user.is_active = False
                user.save()
                student = Student(
                    user=user, organization=student_form.cleaned_data['organization'],
                    country=student_form.cleaned_data['country'],
                    phone_number=student_form.cleaned_data['phone_number'],
                    expired_at=get_expire_date(),
                )
                student.save()
                schema = request.scheme+"://"
                send_email_from_template(
                    'new_user_created_academy', user.email,
                    {
                        "url": request.build_absolute_uri(reverse('confirm_email')),
                        'domain': schema+request.get_host(),
                        "user": user,
                        'student': student
                    },
                    enqueued=True,
                    user=None)
                context['display_form'] = '1'
                context['student_created'] = "on"
                context['show_modal'] = 'on'
            else:
                context['student_form'] = student_form
                context['display_form'] = '2'
                context['show_modal'] = 'on'
    return render(request, "course_detail.html", context)