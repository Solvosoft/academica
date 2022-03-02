# encoding: utf-8
'''
Created on 18/10/2020

@author: allexiusw
'''
import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.contrib import auth

from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse

from django.views.generic import ListView, DeleteView, DetailView
from django.views.decorators.http import require_http_methods

from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django_ajax.decorators import ajax

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template, render_to_string
from django.urls import reverse

from djgentelella.models import MenuItem as DJMenuItem
from async_notifications.utils import send_email_from_template
from chunked_upload.models import ChunkedUpload
from xhtml2pdf import pisa
import django_excel as excel

from matricula.certificate_utils import build_pdf_certificate
from matricula.forms import CategoryCreateForm, CategorySearchForm, \
    CourseSearchForm, CourseCreateForm, EnrollCreateAdminForm, LoginForm, MenuItemSearchForm, \
    MenuItemCreateForm, PeriodCreateForm, PeriodSearchForm, GroupCreateForm, \
    GroupSearchForm, EnrollSearchForm, EnrollCreateForm, StudentAddForm, \
        StudentAdminEditForm, StudentCreateForm, StudentSearchForm, \
    StudentAdminCreateForm, PageCreateForm, PageSearchForm, MenuItemAddForm, \
    PreEnrollAddGroupForm, GroupAddForm, GroupEditForm, PermissionForm, \
    StudentChangePasswordForm
from matricula.models import Category, Course, Period, Group, \
    Enroll, Student, Page, Professor, WaitingList
from matricula.tasks import task_generate_group_certificate
from matricula.views.utils import get_expire_date
from matricula.certificate_utils import link_callback
from matricula.contrib.bills.models import Bill


@method_decorator(permission_required('matricula.view_category'), name='dispatch')
class CategoryList(ListView):
    template_name = "categories/category_list.html"
    paginate_by = 30

    def get_queryset(self):
        queryset = Category.objects.all()
        name = self.request.GET.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CategoryCreateForm()
        context["form_search"] = CategorySearchForm(self.request.GET)
        context['has_data'] = Category.objects.exists()
        return context


@permission_required('matricula.add_category')
def create_category(request):
    context = {}
    if request.method == 'POST':
        name = request.GET.get('name', None)
        if name is not None:
            context['form_search'] = CategorySearchForm(request.GET)
            context['object_list'] = Category.objects.filter(name__icontains=name)
        else:
            context['form_search'] = CategorySearchForm()
            context['object_list'] = Category.objects.all()

        form = CategoryCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            tmpupload = ChunkedUpload.objects.filter(upload_id=request.POST.get("image")).first()
            file = None
            if tmpupload: file = tmpupload.get_uploaded_file()
            category = Category.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                image=file
            )
            category.save()
            if tmpupload: tmpupload.delete()
            messages.success(request, "Registro creado con éxito!")
            context['form'] = CategoryCreateForm()
            return HttpResponseRedirect(reverse('categories'))
        else:
            messages.error(request, "No se ha podido guardar la categoría")
        return render(request, 'categories/category_list.html', context)
    else:
        return HttpResponseRedirect(reverse('categories'))


@method_decorator(permission_required('matricula.delete_category'), name='dispatch')
class CategoryDelete(DeleteView):
    model = Category
    success_url = "/enrrolment/categories/"
    success_message = "Categoría eliminada con éxito"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(CategoryDelete, self).delete(request, *args, **kwargs)


@permission_required('matricula.change_category')
def edit_category(request, pk=None):
    categories = Category.objects.all()
    paginator = Paginator(categories, 30)
    page_number = request.GET.get('page') or 1
    page_obj = paginator.get_page(page_number)
    search_form = CategorySearchForm()
    is_paginated = True if paginator.num_pages > 1 else False
    if pk is not None:
        if request.method == "POST":
            category = Category.objects.get(pk=pk)
            form = CategoryCreateForm(request.POST, instance=category)
            if form.is_valid():
                tmpupload = ChunkedUpload.objects.filter(upload_id=request.POST.get("image")).first()
                file = None
                if tmpupload:
                    file = tmpupload.get_uploaded_file()
                    category.image = file
                category.name = form.cleaned_data['name']
                category.description = form.cleaned_data['description']
                category.save()
                if tmpupload: tmpupload.delete()
                messages.success(request, "Categoría guardada con éxito")
                return HttpResponseRedirect(reverse('categories'))
            else:
                messages.error(request, "Error al actualizar")
        else:
            if request.method == "GET":
                category = Category.objects.get(pk=pk)
                form = CategoryCreateForm(instance=category)
            else:
                form = CategoryCreateForm()
        return render(request, 'categories/category_update.html', {
            'form': form,
            'form_search': search_form,
            'paginator': page_obj,
            'is_paginated': is_paginated
        })
    return HttpResponseRedirect(reverse(request, 'categories'))


@method_decorator(permission_required('matricula.view_course'), name='dispatch')
class CourseList(ListView):
    template_name = "courses/course_list.html"
    model = Course
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = CourseSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['name']:
            queryset = queryset.filter(
                Q(name__icontains=self.form.cleaned_data['name']) |
                Q(content__icontains=self.form.cleaned_data['name']))
        if self.form.cleaned_data['category']:
            queryset = queryset.filter(Q(category__in=self.form.cleaned_data['category']))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_search"] = CourseSearchForm(self.request.GET)
        context['has_data'] = Course.objects.exists()
        return context


@permission_required('matricula.add_course')
def create_course(request):
    context = {}
    if request.method == 'POST':
        form = CourseCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request, "Curso guardado con éxito")
            return HttpResponseRedirect(reverse('enrrolment_courses'))
        else:
            messages.error(request, "Error al guardar curso")
    else:
        context['form'] = CourseCreateForm()
    return render(request, 'courses/course_create.html', context)


@method_decorator(permission_required('matricula.delete_course'), name='dispatch')
class CourseDelete(DeleteView):
    model = Course
    success_url = "/enrrolment/courses/"
    success_message = "Curso eliminado con éxito"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(CourseDelete, self).delete(request, *args, **kwargs)


@permission_required('matricula.change_course')
def edit_course(request, pk=None):
    if pk is not None:
        if request.method == "POST":
            course = Course.objects.get(pk=pk)
            form = CourseCreateForm(request.POST, instance=course)
            if form.is_valid():
                messages.success(request, "Curso guardado con éxito")
                form.save()
                return HttpResponseRedirect(reverse('enrrolment_courses'))
            else:
                messages.error(request, "Error al actualizar")
        else:
            if request.method == "GET":
                course = Course.objects.get(pk=pk)
                form = CourseCreateForm(initial=course.__dict__)
            else:
                form = CourseCreateForm()
        return render(request, 'courses/course_update.html', {'form': form})
    return HttpResponseRedirect(reverse(request, 'enrrolment_courses'))


@permission_required('matricula.can_add_group_course')
def add_group_course(request, pk=None):
    if pk is not None:
        course = Course.objects.get(pk=pk)
        if request.method == "POST":
            form = GroupAddForm(request.POST)
            if form.is_valid():
                group = Group(
                    name=form.cleaned_data['name'],
                    period=form.cleaned_data['period'],
                    course=course,
                    schedule=form.cleaned_data['schedule'],
                    pre_enroll_start=form.cleaned_data['pre_enroll_start'],
                    pre_enroll_finish=form.cleaned_data['pre_enroll_finish'],
                    enroll_start=form.cleaned_data['enroll_start'],
                    enroll_finish=form.cleaned_data['enroll_finish'],
                    is_paid=form.cleaned_data['is_paid'],
                    currency=form.cleaned_data['currency'],
                    cost=form.cleaned_data['cost'],
                    maximum=form.cleaned_data['maximum'],
                    is_open=form.cleaned_data['is_open'],
                    flow=form.cleaned_data['flow'],
                    duration_hours=form.cleaned_data['duration_hours'],
                    expedition_date=form.cleaned_data['expedition_date'],
                )
                group.save()
                group.professors.set(form.cleaned_data['professors'])
                messages.success(request, "Grupo agregado con éxito")
                return HttpResponseRedirect(reverse('enrrolment_courses'))
            else:
                messages.error(request, "Error al crear grupo")
                return render(request, 'courses/course_group_create.html', {'form': form, 'course': course})
        form = GroupAddForm()
        return render(request, 'courses/course_group_create.html', {'form': form, 'course': course})
    return HttpResponseRedirect(reverse('enrrolment_courses'))


@method_decorator(permission_required('djgentelella.view_menuitem'), name='dispatch')
class MenuItemList(ListView):
    template_name = "menuitems/menuitem_list.html"
    model = DJMenuItem
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = MenuItemSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['title']:
            queryset = queryset.filter(
                title__icontains=self.form.cleaned_data['title'])
        if self.form.cleaned_data['parent']:
            queryset = queryset.filter(
                parent__in=self.form.cleaned_data['parent'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_search'] = MenuItemSearchForm(self.request.GET)
        context['has_data'] = DJMenuItem.objects.exists()
        return context


@permission_required('djgentelella.add_menuitem')
def create_menuitem(request):
    context = {}
    if request.method == 'POST':
        form = MenuItemCreateForm(request.POST)
        context['form'] = form
        formPerms = PermissionForm(request.POST)
        if form.is_valid() and formPerms.is_valid():
            menuitem = form.save()
            menuitem.permission.add(*formPerms.cleaned_data['permission'])
            messages.success(request, "Elemento del menú guardado con éxito")
            return HttpResponseRedirect(reverse('menuitems'))
        else:
            messages.error(request, "Error al guardar elemento del menú")
    else:
        context['permsForm'] = PermissionForm()
        context['form'] = MenuItemCreateForm()
    return render(request, 'menuitems/menuitem_create.html', context)


@method_decorator(permission_required('djgentelella.delete_menuitem'), name='dispatch')
class MenuItemDelete(DeleteView):
    model = DJMenuItem
    success_url = "/enrrolment/menuitems"
    success_message = "Menú eliminado con éxito"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        menuitem = self.get_object()
        menuitem.permission.remove(*menuitem.permission.all())
        messages.success(self.request, self.success_message)
        return super(MenuItemDelete, self).delete(request, *args, **kwargs)


@permission_required('djgentelella.change_menuitem')
def edit_menuitem(request, pk=None):
    context = {}
    if pk is not None:
        menu = DJMenuItem.objects.get(pk=pk)
        if request.method == "POST":
            form = MenuItemCreateForm(request.POST, instance=menu)
            context['form'] = form
            formPerms = PermissionForm(request.POST)
            context['formPerms'] = formPerms
            if form.is_valid() and formPerms.is_valid():
                menuitem = form.save()
                menuitem.permission.remove(*menuitem.permission.all())
                menuitem.permission.add(*formPerms.cleaned_data['permission'])
                messages.success(request, "Elemento del menú guardado con éxito")
                return HttpResponseRedirect(reverse('menuitems'))
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'menuitems/menuitem_update.html', context)
        else:
            if request.method == "GET":
                context['form'] = MenuItemCreateForm(initial=menu.__dict__)
                context['permsForm'] = PermissionForm(initial={'permission': menu.permission.all()})
                return render(request, 'menuitems/menuitem_update.html', context)
    return HttpResponseRedirect(reverse('menuitems'))


@method_decorator(permission_required('matricula.view_period'), name='dispatch')
class PeriodList(ListView):
    template_name = "periods/period_list.html"
    model = Period
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = PeriodSearchForm(self.request.GET)
        self.form.is_valid()
        queryset = Period.objects.all()
        if self.form.cleaned_data['name']:
            queryset = queryset.filter(name__icontains=self.form.cleaned_data['name'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PeriodCreateForm()
        context['form_search'] = PeriodSearchForm(self.request.GET)
        context['has_data'] = Period.objects.exists()
        return context


@permission_required('matricula.add_period')
def create_period(request):
    context = {}
    if request.method == 'POST':
        form = PeriodCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request, "Periodo guardado con éxito")
            return HttpResponseRedirect(reverse('periods'))
        else:
            messages.error(request, "Error al guardar el periodo")
            context['object_list'] = Period.objects.all()
            return render(request, 'periods/period_list.html', context)
    return HttpResponseRedirect(reverse('periods'))


@method_decorator(permission_required('matricula.delete_period'), name='dispatch')
class PeriodDelete(DeleteView):
    model = Period
    success_url = "/enrrolment/periods"
    success_message = "Periodo eliminado con éxito"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(PeriodDelete, self).delete(request, *args, **kwargs)


@permission_required('matricula.change_period')
def edit_period(request, pk=None):
    context = {}
    if pk is not None:
        context = {}
        periods = Period.objects.all()
        paginator = Paginator(periods, 30)
        page_number = request.GET.get('page') or 1
        context['paginator'] = paginator.get_page(page_number)
        context['is_paginated'] = True if paginator.num_pages > 1 else False
        if request.method == "POST":
            instance = Period.objects.get(pk=pk)
            form = PeriodCreateForm(request.POST, instance=instance)
            context['form'] = form
            if form.is_valid():
                messages.success(request, "Periodo guardado con éxito")
                form.save()
                return HttpResponseRedirect(reverse('periods'))
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'periods/period_update.html', context)
        else:
            if request.method == "GET":
                instance = Period.objects.get(pk=pk)
                context['form'] = PeriodCreateForm(initial=instance.__dict__)
                context['form_search'] = PeriodSearchForm()
                return render(request, 'periods/period_update.html', context)
    return HttpResponseRedirect(reverse('periods'))


@method_decorator(permission_required('matricula.view_group'), name='dispatch')
class GroupList(ListView):
    template_name = "groups/group_list.html"
    model = Group
    paginate_by = 30

    def get(self, *args, **kwargs):
        if hasattr(self.request.user,
                   'professor') and self.request.user.professor.active or self.request.user.is_active:
            return super(GroupList, self).get(self.request, *args, **kwargs)
        return redirect(reverse('courses'))

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        professor = Professor.objects.filter(user=user).first()

        self.form = GroupSearchForm(self.request.GET)
        self.form.is_valid()
        if 'name' in self.form.cleaned_data and self.form.cleaned_data['name']:
            queryset = queryset.filter(
                Q(name__icontains=self.form.cleaned_data['name']) |
                Q(course__name__icontains=self.form.cleaned_data['name']) |
                Q(course__category__name__icontains=self.form.cleaned_data['name']))
        if 'course' in self.form.cleaned_data and self.form.cleaned_data['course']:
            queryset = queryset.filter(
                course__in=self.form.cleaned_data['course'])
        if 'period' in self.form.cleaned_data  and self.form.cleaned_data['period']:
            queryset = queryset.filter(period__in=self.form.cleaned_data['period'])
        if 'currency' in self.form.cleaned_data and self.form.cleaned_data['currency']:
            queryset = queryset.filter(currency__in=self.form.cleaned_data['currency'])
        if 'category' in self.form.cleaned_data and self.form.cleaned_data['category']:
            queryset = queryset.filter(course__category__in=self.form.cleaned_data['category'])
        if 'open' in self.form.cleaned_data and self.form.cleaned_data['open'] and int(self.form.cleaned_data['open']) != GroupSearchForm.DO_NOT_APPLY:
            if int(self.form.cleaned_data['open']) == GroupSearchForm.OPEN:
                queryset = queryset.filter(is_open=True)
            else:
                queryset = queryset.filter(is_open=False)

        if not user.is_superuser and not user.groups.filter(name=settings.ADMIN_GROUP_NAME).exists():
            if professor:
                queryset = queryset.filter(professors=professor)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        show_qualify_students_button = False

        user = self.request.user
        professor = Professor.objects.filter(user=user).first()

        if professor or self.request.user.is_superuser:
            show_qualify_students_button = True

        context['show_qualify_students_button'] = show_qualify_students_button

        context['form_search'] = GroupSearchForm(self.request.GET)
        context['has_data'] = Group.objects.exists()
        return context


@permission_required('matricula.can_view_pre_enroll_group')
def pre_enroll_group(request, pk=None):
    context = {}
    if pk is not None:
        context = {}
        if request.method == "POST":
            group = Group.objects.get(pk=pk)
            if group:
                form = PreEnrollAddGroupForm(request.POST)
                if form.is_valid():
                    action = request.POST.get('action')
                    if action == "Aperturar matrícula":
                        enrolls = Enroll.objects.filter(pk__in=form.cleaned_data['students'], group=group)
                        emails = []
                        for instance in enrolls:
                            instance.enroll_activate = True
                            instance.save()
                            emails.append(instance.student.user.email)
                        if enrolls.exists():
                            schema = request.scheme + "://"
                            send_email_from_template(
                                'email_open_group', [i for i in emails],
                                {
                                    "url": request.build_absolute_uri(reverse('enrollment')),
                                    "group": group,
                                    'domain': schema + request.get_host(),
                                },
                                enqueued=False, user=None)
                            messages.success(request, "Estudiantes activades para matrícule.")
                        else:
                            messages.error(request, "No se seleccionaron estudiantes.")
                    elif action == "Matricular":
                        enrolls = Enroll.objects.filter(pk__in=form.cleaned_data['students'], group=group)
                        emails = []
                        for instance in enrolls:
                            instance.enroll_activate = True
                            instance.enroll_finished = True
                            instance.save()
                            emails.append(instance.student.user.email)
                        if enrolls.exists():
                            schema = request.scheme + "://"
                            send_email_from_template(
                                'email_enroll_success', [i for i in emails],
                                {
                                    "url": request.build_absolute_uri(reverse('enrollment')),
                                    "group": group,
                                    'domain': schema + request.get_host(),
                                },
                                enqueued=True, user=None)
                            messages.success(request, "Transacción realizada satisfactoriamente.")
                        else:
                            messages.error(request, "No se seleccionaron estudiantes.")
                    elif action == "Rechazar pre-inscripción":
                        enrolls = Enroll.objects.filter(pk__in=form.cleaned_data['students'], group=group)
                        emails = []
                        for instance in enrolls:
                            instance.rejected = True
                            instance.enroll_finished = False
                            instance.enroll_activate = False
                            instance.paid_excluded = False
                            instance.save()
                            emails.append(instance.student.user.email)
                        schema = request.scheme + "://"
                        if enrolls.exists():
                            send_email_from_template(
                                'email_enroll_rejected', [i for i in emails],
                                {
                                    "url": request.build_absolute_uri(reverse('enrollment')),
                                    "group": group,
                                    'domain': schema + request.get_host(),
                                },
                                enqueued=False, user=None)
                            messages.success(request, "Estudiantes notificades con éxito")
                        else:
                            messages.error(request, "No se seleccionaron estudiantes.")
                    elif action == "Agregar a lista de espera":
                        students = form.cleaned_data['students']
                        students_pk = list(students.values_list('student', flat=True))
                        if len(students_pk)>0:
                            enrolls = set(WaitingList.objects.filter(
                                student__pk__in=students_pk, group=group).values_list("student__pk",flat=True))
                            for i in enrolls:
                                try:
                                    students_pk.remove(i)
                                except IndexError:
                                    pass
                            waiting_list = []
                            list_students = Student.objects.filter(pk__in=students_pk)
                            for i in list_students:
                                waiting_list.append(WaitingList(student=i, group=group))
                            WaitingList.objects.bulk_create(waiting_list)
                            messages.success(request, "Estudiantes agregados a la lista de espera.")
                        else:
                            messages.error(request, "No se seleccionaron estudiantes.")
                    return HttpResponseRedirect(reverse('pre_enroll_group', args=[pk]))
            messages.error(request, "Error al realizar la acción")
            return HttpResponseRedirect(reverse('pre_enroll_group', args=[pk]))
        else:
            if request.method == "GET":
                instance = Group.objects.get(pk=pk)
                context['object'] = instance
                context['pre_enroll_list'] = Enroll.objects.filter(
                    group=instance, enroll_finished=False, rejected=False)
                return render(
                    request, 'groups/pre_enroll_group_list.html', context)
    return HttpResponseRedirect(reverse('periods'))


@permission_required('matricula.add_group')
def create_group(request):
    context = {}
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if request.POST.get("is_paid") == 'on':
            form.fields['currency'].required = True
        context['form'] = form
        if form.is_valid():
            preenroll = form.cleaned_data['pre_enroll_finish'] >= form.cleaned_data['pre_enroll_start'] 
            enroll = form.cleaned_data['enroll_finish'] >= form.cleaned_data['enroll_start'] 
            in_ranges = form.cleaned_data['pre_enroll_finish'] <= form.cleaned_data['enroll_start']
            if preenroll and enroll and in_ranges:
                group = Group(
                    name=form.cleaned_data['name'],
                    course=form.cleaned_data['course'],
                    period=form.cleaned_data['period'],
                    schedule=form.cleaned_data['schedule'],
                    pre_enroll_start=form.cleaned_data['pre_enroll_start'],
                    pre_enroll_finish=form.cleaned_data['pre_enroll_finish'],
                    enroll_start=form.cleaned_data['enroll_start'],
                    enroll_finish=form.cleaned_data['enroll_finish'],
                    is_paid=form.cleaned_data['is_paid'],
                    currency=form.cleaned_data['currency'],
                    cost=form.cleaned_data['cost'],
                    maximum=form.cleaned_data['maximum'],
                    flow=form.cleaned_data['flow'],
                    expedition_date=form.cleaned_data['expedition_date'],
                    duration_hours=form.cleaned_data['duration_hours'],
                )
                group.save()
                group.professors.set(form.cleaned_data['professors'])
                messages.success(request, "Grupo guardado con éxito")
            else:
                msg = "Fechas incorrectas en prematrícula. La fecha de inicio debe ser menor a la fecha fin."
                if not enroll: msg = "Fechas incorrectas en matrícula. La fecha de inicio debe ser menor a la fecha fin."
                if not in_ranges: msg = "Error en rangos de fechas. Pre-matrícula debe finalizar antes de la fecha de inicio de matrícula."
                messages.error(request, msg)
                return render(request, 'groups/group_create.html', context)
            return HttpResponseRedirect(reverse('groups_enroll'))
        else:
            messages.error(request, "Error al guardar grupo")
    else:
        context['form'] = GroupCreateForm()
    return render(request, 'groups/group_create.html', context)


@method_decorator(permission_required('matricula.delete_group'), name='dispatch')
class GroupDelete(DeleteView):
    model = Group
    success_url = "/enrrolment/groups"
    success_message = "Grupo eliminado con éxito"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(GroupDelete, self).delete(request, *args, **kwargs)


@permission_required('matricula.change_group')
def edit_group(request, pk=None):
    if pk is not None:
        instance = Group.objects.get(pk=pk)
        if request.method == "POST":
            form = GroupEditForm(request.POST, instance=instance)
            if request.POST.get("is_paid") == 'on':
                form.fields['currency'].required = True
            if form.is_valid():
                preenroll = form.cleaned_data['pre_enroll_finish'] >= form.cleaned_data['pre_enroll_start'] 
                enroll = form.cleaned_data['enroll_finish'] >= form.cleaned_data['enroll_start'] 
                in_ranges = form.cleaned_data['pre_enroll_finish'] <= form.cleaned_data['enroll_start']
                if preenroll and enroll and in_ranges:
                    form.save()
                    messages.success(request, "Grupo guardado con éxito")
                    return HttpResponseRedirect(reverse('groups_enroll'))
                else:
                    msg = "Fechas incorrectas en prematrícula. La fecha de inicio debe ser menor a la fecha fin."
                    if not enroll: msg = "Fechas incorrectas en matrícula. La fecha de inicio debe ser menor a la fecha fin."
                    if not in_ranges: msg = "Error en rangos de fechas. Pre-matrícula debe finalizar antes de la fecha de inicio de matrícula."
                    messages.error(request, msg)
                    return render(request, 'groups/group_update.html', {'form': form})
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'groups/group_update.html', {'form': form})
        else:
            if request.method == "GET":
                info = instance.__dict__
                info['professors'] = instance.professors.all()
                form = GroupEditForm(initial=instance.__dict__)
                return render(request, 'groups/group_update.html', {'form': form})
    return HttpResponseRedirect(reverse('groups_enroll'))


@permission_required('matricula.can_export_enrolled_group')
def export_group(request, pk=None):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_list.csv"'
    writer = csv.writer(response, delimiter=';', quotechar='|')
    response.write(u'\ufeff'.encode('utf8'))
    if pk is not None:
        group = get_object_or_404(Group, pk=pk)
        enrolls = Enroll.objects.filter(group=group, enroll_finished=True)
        if group.is_paid:
            enrolls = enrolls.filter(bill__is_paid=True)
        writer.writerow([
            'username',
            'firstname',
            'lastname',
            'email',
            'institution',
            'country',
            'city',
            "course1"])
        for enroll in enrolls:
            first_name = enroll.student.user.first_name if enroll.student.user.first_name != "" else "default"
            last_name = enroll.student.user.last_name if enroll.student.user.last_name != "" else "default"
            organizations = enroll.student.organizations
            org = "Sin organización"
            if organizations:
                org = " - ".join([x['value'] for x in enroll.student.organizations if 'value' in x])
            writer.writerow([
                enroll.student.user.username,
                first_name,
                last_name,
                enroll.student.user.email,
                org,
                enroll.student.country.code,
                enroll.student.city,
                group.name])
        return response
    return HttpResponseRedirect(reverse('groups_enroll'))


@permission_required('matricula.can_list_students_group')
def list_students_group(request, pk=None):
    context = {}
    show_buttons_certificates = False
    show_column_action = False
    course_status = request.GET.get('course_status', '')
    filters = {}
    if course_status in ('approved', 'reproved'):
        filters['course_status']=course_status
    if pk != None:
        context = {}
        instance = get_object_or_404(Group, pk=pk)
        filters['group'] = instance
        filters['enroll_finished'] = True
        enroll_list = Enroll.objects.filter(**filters)
        if instance.is_paid:
            enroll_list = enroll_list.filter(Q(bill__is_paid=True) | Q(paid_excluded=True))


        context['object'] = enroll_list
        context['group'] = instance
        approved_students = enroll_list.filter(course_status="approved")
        enroll_finished = enroll_list.filter(enroll_finished=True)
        enroll_list_with_certificates = enroll_list.filter(pdf_certificate__isnull=False).exclude(pdf_certificate="")

        for enroll in enroll_list:

            if enroll.pdf_certificate is None or enroll.pdf_certificate == "" and approved_students and enroll_finished and request.user.is_superuser:
                show_buttons_certificates = True
                break

        if enroll_list_with_certificates:
            show_column_action = True

        context['show_column_action'] = show_column_action
        context['show_buttons_certificates'] = show_buttons_certificates
        return render(request, 'groups/group_students_list.html', context)
    return HttpResponseRedirect(reverse('groups'))


@permission_required('matricula.can_open_group')
def open_group(request, pk):
    group = Group.objects.get(pk=pk)
    enrolls = Enroll.objects.filter(group=group)
    enrolls.update(enroll_activate=True)
    group.is_open = True
    if request.GET.get('sendemail', '0') == '1':
        group.notified_open = True
        schema = request.scheme + "://"
        send_email_from_template(
            'email_open_group',
            [enroll.student.user.email for enroll in enrolls],
            {
                "url": request.build_absolute_uri(
                    reverse('course', args=[group.course.pk])),
                "group": group,
                'domain': schema + request.get_host(),
            },
            enqueued=False,
            user=None)
    group.save()
    messages.success(request, "Grupo aperturado con éxito")
    return HttpResponseRedirect(reverse('list_students_group', args=[pk, ]))


@permission_required('matricula.can_open_group')
def email_enrolled_group(request, pk):
    group = Group.objects.get(pk=pk)
    enrolls = Enroll.objects.filter(group=group, enroll_finished=True)
    for enroll in enrolls:
        schema = request.scheme + "://"
        send_email_from_template(
            'email_enroll_success',
            [enroll.student.user.email],
            {
                "url": request.build_absolute_uri(
                    reverse('course', args=[group.course.pk])),
                "group": group,
                'domain': schema + request.get_host(),
            },
            enqueued=True,
            user=None)
    messages.success(request, "Notificaciones enviadas con éxito")
    return HttpResponseRedirect(reverse('list_students_group', args=[pk, ]))

@permission_required('matricula.can_close_group')
def close_group(request, pk):
    group = Group.objects.get(pk=pk)
    enrolls = Enroll.objects.filter(group=group)
    enrolls.update(enroll_activate=False)
    group.is_open = False
    if request.GET.get('sendemail', '0') == '1':
        schema = request.scheme + "://"
        group.notified_close = True
        send_email_from_template(
            'email_close_group',
            [enroll.student.user.email for enroll in enrolls],
            {
                "url": request.build_absolute_uri(
                    reverse('courses')),
                "group": group,
                'domain': schema + request.get_host(),
            },
            enqueued=False,
            user=None)
    group.save()
    messages.success(request, "Grupo cerrado con éxito")
    return HttpResponseRedirect(reverse('list_students_group', args=[pk, ]))


@permission_required('matricula.can_view_pdf_enrolled_group')
def export_enrolled_group(request, pk=None):
    group = get_object_or_404(Group, pk=pk)
    attrs = {'group__pk': pk}
    attrs['enroll_finished'] = False
    if request.GET.get('finished', '0') == '1':
        attrs['enroll_finished'] = True
    student_list = Enroll.objects.filter(**attrs)
    template = get_template('Pdf/student_list.html')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    html = template.render({
        'student_list': student_list, 'group': group, **attrs})
    pisa_status = pisa.CreatePDF(
        html, dest=response, link_callback=link_callback)
    if not pisa_status.err:
        return response
    return HttpResponse("Error " + str(pisa_status.err) + "  " + html)


@method_decorator(permission_required('matricula.view_enroll'), name='dispatch')
class EnrollList(ListView):
    template_name = "enrolls/enroll_list.html"
    model = Enroll
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = EnrollSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['student']:
            queryset = queryset.filter(student__in=self.form.cleaned_data['student'])
        if self.form.cleaned_data['group']:
            queryset = queryset.filter(group__in=self.form.cleaned_data['group'])
        if self.form.cleaned_data['paid']:
            queryset = queryset.filter(bill__is_paid=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_search'] = EnrollSearchForm(self.request.GET)
        context['has_data'] = Enroll.objects.exists()
        return context


@permission_required('matricula.add_enroll')
def create_enroll(request):
    context = {}
    if request.method == 'POST':
        form = EnrollCreateAdminForm(request.POST)
        context['form'] = form
        if form.is_valid():
            group = form.cleaned_data['group']
            student = form.cleaned_data['student']
            enroll_exists = Enroll.objects.filter(student=student, group=group).exists()
            if enroll_exists:
                messages.error(request, "Error al guardar la matrícula ya existe")
                return render(request, 'enrolls/enroll_create.html', context)
            schema = request.scheme + "://"
            template = 'email_preenroll_success'
            if form.cleaned_data['enroll_finished']:
                template = 'email_enroll_success'
            send_email_from_template(
                template, [student.user.email],
                {
                    "url": request.build_absolute_uri(reverse('enrollment')),
                    "group": group,
                    'domain': schema + request.get_host(),
                },
                enqueued=False, user=None)
            enroll = form.save()
            if enroll.paid_excluded:
                send_email_from_template(
                    'enroll_paid_excluded', student.user.email,
                    {
                        "url": request.build_absolute_uri(reverse('login')),
                        'domain': schema+request.get_host(),
                        "user": student.user,
                        'group': enroll.group
                    },
                    enqueued=False,
                    user=None)
            messages.success(request, "Matrícula guardada con éxito")
            return HttpResponseRedirect(reverse('enrolls'))
        else:
            messages.error(request, "Error al guardar matrícula")
    else:
        context['form'] = EnrollCreateAdminForm()
    return render(request, 'enrolls/enroll_create.html', context)


@permission_required('matricula.change_enroll')
def edit_enroll(request, pk=None):
    if pk is not None:
        if request.method == "POST":
            instance = Enroll.objects.get(pk=pk)
            enroll_finished = instance.enroll_finished
            paid_excluded = instance.paid_excluded
            form = EnrollCreateAdminForm(request.POST, instance=instance)
            if form.is_valid():
                schema = request.scheme + "://"
                student = form.cleaned_data['student']
                group = form.cleaned_data['group']
                enroll_exists = Enroll.objects.filter(
                    student=student, group=group).exclude(pk=instance.pk).exists()
                if enroll_exists:
                    messages.error(request, "Error al actualizar matrícula duplicada")
                    return render(request, 'enrolls/enroll_update.html', {'form': form})
                if not enroll_finished and form.cleaned_data['enroll_finished']:
                    send_email_from_template(
                        'email_enroll_success', [student.user.email],
                        {
                            "url": request.build_absolute_uri(reverse('enrollment')),
                            "group": group,
                            'domain': schema + request.get_host(),
                            'hours_to_pay': settings.HOURS_TO_PAY,
                        },
                        enqueued=False, user=None)
                if not paid_excluded and form.cleaned_data['paid_excluded']:
                    Bill.objects.filter(enrollment=instance).delete()
                    instance.bill_created = False
                    instance.save()
                    send_email_from_template(
                        'enroll_paid_excluded', student.user.email,
                        {
                            "url": request.build_absolute_uri(reverse('login')),
                            'domain': schema+request.get_host(),
                            "user": student.user,
                            'group': instance.group
                        },
                        enqueued=False,
                        user=None)
                messages.success(request, "Matrícula guardada con éxito")
                form.save()
                return HttpResponseRedirect(reverse('enrolls'))
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'enrolls/enroll_update.html', {'form': form})
        else:
            if request.method == "GET":
                instance = get_object_or_404(Enroll, pk=pk)
                form = EnrollCreateAdminForm(instance=instance)
                return render(request, 'enrolls/enroll_update.html', {'form': form})
    return HttpResponseRedirect(reverse('enrolls'))


@permission_required('matricula.can_recovery_pass_student')
def notify_rejected(request, pk=None):
    enroll = get_object_or_404(Enroll, pk=pk)
    schema = request.scheme + "://"
    send_email_from_template(
        'email_enroll_rejected', enroll.student.user.email,
        {
            "url": request.build_absolute_uri(reverse('enrollment')),
            "group": enroll.group,
            'domain': schema + request.get_host(),
        },
        enqueued=False, user=None)
    messages.success(
        request, "Se ha notificado al usuarie que la matrícula ha sido rechazada")
    return HttpResponseRedirect(reverse('enrolls'))

@permission_required('matricula.can_recovery_pass_student')
def notify_enroll_success(request, pk=None):
    enroll = get_object_or_404(Enroll, pk=pk)
    schema = request.scheme + "://"
    send_email_from_template(
        'email_enroll_success', enroll.student.user.email,
        {
            "url": request.build_absolute_uri(reverse('enrollment')),
            "group": enroll.group,
            'domain': schema + request.get_host(),
        },
        enqueued=False, user=None)
    messages.success(
        request, "Se ha enviado el correo con éxito")
    return HttpResponseRedirect(reverse('enrolls'))


@method_decorator(permission_required('matricula.delete_enroll'), name='dispatch')
class EnrollDelete(DeleteView):
    model = Enroll
    success_url = "/enrrolment/enrolls"
    success_message = "Matrícula eliminada con éxito"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(EnrollDelete, self).delete(request, *args, **kwargs)


@method_decorator(permission_required('matricula.view_student'), name='dispatch')
class StudentList(ListView):
    template_name = "students/student_list.html"
    model = Student
    paginate_by = 30

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = StudentSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['student']:
            queryset = queryset.filter(
                pk__in=self.form.cleaned_data['student'])
        if self.form.cleaned_data['active']:
            queryset = queryset.filter(
                user__is_active=self.form.cleaned_data['active'])
        if self.form.cleaned_data['group']:
            queryset = queryset.filter(
                enroll__group=self.form.cleaned_data['group'])
        if self.form.cleaned_data['organization']:
            queryset = queryset.filter(
                organization__icontains=self.form.cleaned_data['organization'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_search'] = StudentSearchForm(self.request.GET)
        context['has_data'] = Student.objects.exists()
        return context

    def get(self, request, *args, **kwargs):
        if request.GET.get("action")=="Exportar correos":
            try:
                query_sets = self.get_queryset()
                column_names = [
                    'user__first_name',
                    'user__last_name',
                    'user__email',
                    'country__name',
                    'city',
                    'phone_number',
                ]
                sheet_header = [
                    'Nombres',
                    'Apellidos',
                    'Correo electrónico',
                    'País',
                    'Ciudad',
                    'Teléfono',
                ]
                sheet = excel.pe.get_sheet(query_sets=query_sets, column_names=column_names)
                sheet.name_columns_by_row(0)
                sheet.colnames = sheet_header
                return excel.make_response(sheet, 'xls',file_name='students')
            except:
                messages.error(request, "No fue posible exportar el excel por que no hay datos a mostrar")
        return super().get(request, *args, **kwargs)


@permission_required('matricula.add_student')
def create_student(request):
    context = {'form_show': 'first'}
    if request.method == 'POST':
        user_created = request.POST.get('user', None)
        if (user_created is not None):
            form_user = StudentAddForm(request.POST)
            context['form_user'] = form_user
            if form_user.is_valid():
                student = Student(
                    user=form_user.cleaned_data['user'],
                    organization=form_user.cleaned_data['organization2'],
                    created_at=now(), confirmed_at=now(),
                    phone_number=form_user.cleaned_data['phone_number'],
                    country=form_user.cleaned_data['country2'],
                    city=form_user.cleaned_data['city2'],
                    expired_at=get_expire_date())
                student.save()
                schema = request.scheme + "://"
                send_email_from_template(
                    'set_email_first_academy', student.user.email,
                    {
                        'domain': schema + request.get_host(),
                        "url": request.build_absolute_uri(
                            reverse('recover_password')),
                        'student': student,
                    },
                    enqueued=False,
                    user=None)
                messages.success(request, "Estudiante guardade con éxito")
                return HttpResponseRedirect(reverse('students'))
            else:
                messages.error(request, "Error al guardar Estudiante")
                context['form'] = StudentAdminCreateForm()
            context['form_show'] = 'last'
        else:
            form = StudentAdminCreateForm(request.POST)
            context['form'] = form
            if form.is_valid():
                user = User(
                    username=form.cleaned_data['username'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    is_active=True)
                user.save()
                student = Student(
                    user=user, organization=form.cleaned_data['organization'],
                    created_at=now(), confirmed_at=now(),
                    phone_number=form.cleaned_data['phone_number'],
                    country=form.cleaned_data['country'],
                    city=form.cleaned_data['city'],
                    expired_at=get_expire_date())
                student.save()
                schema = request.scheme + "://"
                send_email_from_template(
                    'set_email_first_academy', user.email,
                    {
                        'domain': schema + request.get_host(),
                        "url": request.build_absolute_uri(
                            reverse('recover_password')),
                        'student': student,
                    },
                    enqueued=False,
                    user=None)
                messages.success(request, "Estudiante guardade con éxito")
                return HttpResponseRedirect(reverse('students'))
            else:
                context['form_user'] = StudentAddForm()
                messages.error(request, "Error al guardar Estudiante")
    else:
        context['form'] = StudentAdminCreateForm()
        context['form_user'] = StudentAddForm()
    return render(request, 'students/student_create.html', context)


@permission_required('matricula.change_student')
def edit_student(request, pk=None):
    if pk is not None:
        if request.method == "POST":
            instance = User.objects.get(pk=pk)
            form = StudentAdminEditForm(request.POST, instance=instance)
            if form.is_valid():
                messages.success(request, "Estudiante guardade con éxito")
                form.save()
                instance.student.organization = form.cleaned_data['organization']
                instance.student.country = form.cleaned_data['country']
                instance.student.city = form.cleaned_data['city']
                instance.student.phone_number = form.cleaned_data['phone_number']
                instance.student.save()
                return HttpResponseRedirect(reverse('students'))
            else:
                messages.error(request, "Error al actualizar")
                return render(
                    request, 'students/student_update.html', {'form': form})
        else:
            if request.method == "GET":
                instance = User.objects.get(pk=pk)
                inst = instance.__dict__
                inst['country'] = instance.student.country
                inst['city'] = instance.student.city
                inst['phone_number'] = instance.student.phone_number
                inst['organization'] = instance.student.organization
                inst['edit'] = True
                form = StudentAdminEditForm(initial=inst)
                return render(
                    request, 'students/student_update.html', {'form': form})
    return HttpResponseRedirect(reverse('students'))


@permission_required('matricula.change_student')
def edit_password_student(request, pk=None):
    if pk is not None:
        if request.method == "POST":
            instance = User.objects.get(pk=pk)
            form = StudentChangePasswordForm(request.POST, instance=instance)
            if form.is_valid():
                instance.set_password(form.cleaned_data['password'])
                instance.save()
                messages.success(request, "Contraseña actualizada con éxito")
                return HttpResponseRedirect(reverse('students'))
            else:
                messages.error(request, "Error al actualizar")
                return render(
                    request, 'students/student_change_password.html', {'form': form})
        else:
            if request.method == "GET":
                instance = User.objects.get(pk=pk)
                inst = instance.__dict__
                form = StudentChangePasswordForm(initial=inst)
                return render(
                    request, 'students/student_change_password.html', {'form': form})
    return HttpResponseRedirect(reverse('students'))


@method_decorator(permission_required('matricula.delete_student'), name='dispatch')
class StudentDelete(DeleteView):
    model = Student
    success_url = "/enrrolment/students"
    success_message = "Estudiante eliminada con éxito"

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        professor = hasattr(student.user, 'professor')
        admin = student.user.groups.filter(name=settings.ADMIN_GROUP_NAME)
        if professor or admin.exists():
            student.delete()
            messages.success(self.request, _("Student role removed successfuly"))
            return HttpResponseRedirect(self.success_url)
        student.user.delete()
        student.delete()
        messages.success(self.request, self.success_message)
        return HttpResponseRedirect(self.success_url)


@method_decorator(permission_required('matricula.view_student'), name='dispatch')
class StudentDetailView(DetailView):
    model = Student
    template_name = 'students/student_detail.html'


@method_decorator(permission_required('matricula.view_student'), name='dispatch')
class GroupDetailView(DetailView):
    model = Group
    template_name = 'groups/waitinglist_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EnrollCreateForm(
            initial={'group': self.get_object(), 'enroll_finished':True})
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        form = EnrollCreateForm(request.POST, initial={'group':self.object})
        context['form'] = form
        if form.is_valid():
            pk = form.cleaned_data['student_pk']
            student = get_object_or_404(Student, pk=pk)
            group = form.cleaned_data['group']
            waitinglist = WaitingList.objects.filter(group=self.object, student=student)
            enroll = Enroll.objects.filter(group=group, student=student)
            if enroll.exists():
                if enroll.first().enroll_finished:
                    messages.success(request, 'Proceso de matrícula finalizado con éxito')
                else:
                    update = EnrollCreateForm(request.POST, instance=enroll.first())
                    if update.is_valid():
                        instance = update.save()
                        if instance.enroll_finished:
                            messages.success(request, 'Proceso de matrícula finalizado con éxito')
                        else:
                            messages.success(request, "La pre-inscripción fue actualizada correctamente.")
                waitinglist.delete()
            else:
                schema = request.scheme + "://"
                template = 'email_preenroll_success'
                paid_excluded = form.cleaned_data['paid_excluded']
                if form.cleaned_data['enroll_finished']:
                    template = 'email_enroll_success'
                send_email_from_template(
                    template, [student.user.email],
                    {
                        "url": request.build_absolute_uri(reverse('enrollment')),
                        "group": group,
                        'domain': schema + request.get_host(),
                    },
                    enqueued=False, user=None)
                instance = form.save(commit=False)
                instance.student=student
                instance.save()
                if paid_excluded:
                    send_email_from_template(
                    'enroll_paid_excluded', student.user.email,
                    {
                        "url": request.build_absolute_uri(reverse('login')),
                        'domain': schema+request.get_host(),
                        "user": student.user,
                        'group': group
                    },
                    enqueued=False,
                    user=None)
                if instance.enroll_finished:
                    messages.success(request, f"La matrícula fue realizada con éxito")
                else:
                    messages.success(request, "La pre-inscripción fue actualizada correctamente.")
            WaitingList.objects.filter(group=self.object, student=student).delete()
        else:
            context['errors'] = True
            messages.error(request, "Error al guardar los datos")
        return self.render_to_response(context=context)


@permission_required('matricula.view_student')
def export_waitinglist_xls(request, pk=None):
    group_name = 'waitinglist'
    waitinglist = None
    if pk is not None:
        item = Group.objects.get(pk=pk)
        group_name += "-" + item.name
        waitinglist = WaitingList.objects.filter(group=pk)
    column_names = [
        'group__name', 'student__user__username','student__user__email',
        'student__user__first_name', 'student__user__last_name','created_at']
    if not waitinglist.count()>0:
        messages.error(request, "No hay registros para exportar")
        return redirect(reverse('waitinglist_group', kwargs={"pk": pk}))
    else:
        return excel.make_response_from_query_sets(
            waitinglist, column_names, 'xlsx', file_name=group_name)


@permission_required('matricula.can_recovery_pass_student')
def recovery_pass_student(request, pk=None):
    if (pk is not None):
        student = Student.objects.get(pk=pk)
        if student:
            schema = request.scheme + "://"
            send_email_from_template(
                'email_recovery_academy', student.user.email, {
                    'url': request.build_absolute_uri(
                        reverse('recover_password')),
                    'domain': schema + request.get_host(),
                    'user': student.user,
                    'student': student,
                },
                enqueued=False,
                user=None)
            messages.success(
                request, "Se ha enviado correo de recuperación de contraseña.")
        else:
            messages.error(request, "El usuarie no fue encontrade")
    return HttpResponseRedirect(reverse('students'))


@method_decorator(permission_required('matricula.view_page'), name='dispatch')
class PageList(ListView):
    template_name = "pages/page_list.html"
    model = Page
    paginate_by = 30

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(PageList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = PageSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['slug']:
            queryset = queryset.filter(
                Q(slug__icontains=self.form.cleaned_data['slug']) |
                Q(title__icontains=self.form.cleaned_data['slug']))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_search'] = PageSearchForm(self.request.GET)
        pages = []
        for page in self.get_queryset():
            page.menu = DJMenuItem.objects.filter(
                url_name=reverse('pages_view', kwargs={'slug': page.slug})).first()
            pages.append(page)
        context['object_list'] = pages
        return context


@permission_required('matricula.add_page')
def create_page(request):
    context = {}
    if request.method == 'POST':
        form = PageCreateForm(request.POST)
        context['form'] = form
        menu_form = MenuItemAddForm(request.POST)
        context['menu_form'] = menu_form
        if form.is_valid():
            page = Page(
                title=form.cleaned_data['title'],
                content=form.cleaned_data['content'],
                slug=form.cleaned_data['slug'])
            page.save()
            if form.cleaned_data['create_menu']:
                menu_form.is_valid()
                menu = DJMenuItem(
                    title=page.title,
                    category='main',
                    url_name=reverse('pages_view', kwargs={'slug': page.slug}),
                    is_reversed=False,
                    reversed_args='',
                    reversed_kwargs='',
                    icon='',
                    only_icon=False,
                    parent=menu_form.cleaned_data['parent'],
                    is_widget=False
                )
                menu.save()
            messages.success(request, "Página guardada con éxito")
            return HttpResponseRedirect(reverse('pages'))
        else:
            messages.error(request, "Error al guardar la página")
    else:
        context['form'] = PageCreateForm()
        context['menu_form'] = MenuItemAddForm()
    return render(request, 'pages/page_create.html', context)


@permission_required('matricula.add_page')
def create_menupage(request, pk=None):
    context = {}
    if pk is not None:
        if request.method == 'POST':
            form = MenuItemAddForm(request.POST)
            if form.is_valid():
                page = Page.objects.get(pk=pk)
                menu = DJMenuItem(
                    title=page.title,
                    category='main',
                    url_name=reverse('pages_view', kwargs={'slug': page.slug}),
                    is_reversed=False,
                    reversed_args='',
                    reversed_kwargs='',
                    icon='',
                    only_icon=False,
                    parent=form.cleaned_data['parent'],
                    is_widget=False
                )
                menu.save()
                messages.success(request, "Menú guardado con éxito")
                return HttpResponseRedirect(reverse('pages'))
            else:
                messages.error(request, "Error al guardar el menú")
        else:
            context['form'] = MenuItemAddForm()
    else:
        messages.error("Página no encontrada")
        return HttpResponseRedirect(reverse('pages'))
    return render(request, 'pages/menupage_create.html', context)


@permission_required('matricula.change_page')
def edit_page(request, pk=None):
    context = {}
    if pk is not None:
        if request.method == "POST":
            instance = Page.objects.get(pk=pk)
            form = PageCreateForm(request.POST, instance=instance)
            if form.is_valid():
                messages.success(request, "Página guardada con éxito")
                form.save()
                return HttpResponseRedirect(reverse('pages'))
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'pages/page_update.html', {'form': form})
        else:
            if request.method == "GET":
                instance = Page.objects.get(pk=pk)
                context['form'] = PageCreateForm(initial=instance.__dict__, edit_page=True)
                return render(request, 'pages/page_update.html', context)
    return HttpResponseRedirect(reverse('pages'))


@method_decorator(permission_required('matricula.delete_page'), name='dispatch')
class PageDelete(DeleteView):
    model = Page
    success_url = '/enrrolment/pages'
    success_message = "Página eliminada con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(PageDelete, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        page = self.get_object()
        DJMenuItem.objects.filter(url_name="/enrrolment_pages/" + page.slug).delete()
        messages.success(self.request, self.success_message)
        return super(PageDelete, self).delete(request, *args, **kwargs)


@method_decorator(permission_required('matricula.delete_page'), name='dispatch')
class MenuPageDelete(DeleteView):
    model = DJMenuItem
    success_url = "/enrrolment/pages"
    success_message = "Menú eliminado con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(MenuPageDelete, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MenuPageDelete, self).delete(request, *args, **kwargs)


@staff_member_required
def build_pdf_certificate_view(request, pk):
    enroll = get_object_or_404(Enroll, pk=pk)
    build_pdf_certificate(enroll)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="' + str(enroll.group) + "-" + str(enroll.student) + '.pdf"'
    response.write(enroll.pdf_certificate.read())
    return response


@staff_member_required
def regenerate_certificate(request, pk_group, pk):
    enroll = get_object_or_404(Enroll, pk=pk)
    build_pdf_certificate(enroll)
    messages.success(request, "Certificado regenerado con éxito.")
    return redirect('list_students_group', pk=pk_group)


@staff_member_required
def build_pdf_certificate_list(request, pk):
    get_object_or_404(Group, pk=pk)
    task_generate_group_certificate.delay(pk)
    messages.success(request, "Certificados se han iniciado a procesar, regrese en unos minutos y refresque la página.")
    return redirect("list_students_group", pk=pk)


@ajax
@require_http_methods(["GET"])
def get_forms_modal(request):
    context = {
        'login_form': LoginForm(),
        'student_form': StudentCreateForm(),
    }
    response = {
        'result': render_to_string(
            'gentelella/registration/login_modal.html', context
        ),
        'display_form': request.GET.get('modal',"1"),
    }
    return JsonResponse(response)


@ajax
@require_http_methods(["POST"])
def do_login(request):
    form = LoginForm(request.POST)
    response = {}
    if form.is_valid():
        user = auth.authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password2']
        )
        if user is not None and user.is_active:
            auth.login(request, user)
            response['result'] = 'ok'
        else:
            context = {
                'login_form': form,
                'student_form': StudentCreateForm(),
            }
            response['result'] = 'error-nonfield'
            response['data'] = render_to_string('gentelella/registration/login_modal.html', context)
            response['display_form'] = request.GET.get('modal',"1"),
            response['message'] = "Usuario y/o contraseña incorrectos o usuario deshabilitado"
    else:
        context = {
            'login_form': form,
            'student_form': StudentCreateForm(),
        }
        response['result'] = 'error'
        response['data'] = render_to_string('gentelella/registration/login_modal.html', context)
        response['display_form'] = request.GET.get('modal',"1"),
        response['message'] = 'Los campos del formulario son requeridos.'
    return JsonResponse(response)


@ajax
@require_http_methods(["POST"])
def create_student_ajax(request):
    form = StudentCreateForm(request.POST)
    response = {}
    if form.is_valid():
        user = User.objects.create_user(
                username=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'])
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.is_active = False
        user.save()
        student = Student(
            user=user, organization=form.cleaned_data['organization'],
            country=form.cleaned_data['country'],
            phone_number=form.cleaned_data['phone_number'],
            expired_at=get_expire_date(),)
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
            enqueued=False,
            user=None)
        context = {
            'login_form': LoginForm(),
            'student_form': StudentCreateForm(),
        }
        response['result'] = 'ok'
        response['key'] = student.key
        response['data'] = render_to_string('gentelella/registration/login_modal.html', context)
        response['display_form'] = "1",
    else:
        context = {
            'login_form': LoginForm(),
            'student_form': form,
        }
        response['data'] = render_to_string('gentelella/registration/login_modal.html', context)
        response['display_form'] = request.GET.get('modal',"2"),
        response['result'] = 'error'
        response['message'] = 'Los campos del formulario son requiridos.'
        response['errors'] = form.errors
    return JsonResponse(response)


@ajax
@require_http_methods(['GET'])
def student_isactive(request, key):
    student = get_object_or_404(Student, key=key)
    result = {'result': 'ok', 'is_active':student.user.is_active}
    return JsonResponse(result)


@permission_required('matricula.view_group')
def view_organizations_countries_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    context = {
        "title": group.name or '',
        "url_countries": reverse('countries_group_api-list')+"?pk=%d"%(pk),
        "url_organizations": reverse('organizations_group_api-list')+"?pk=%d"%(pk)
    }
    return render(request, "groups/organizations_countries.html", context=context)
