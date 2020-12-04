# encoding: utf-8
'''
Created on 18/10/2020

@author: allexiusw
'''
import csv
import io
import os
from django.conf import settings
from django.views.generic import ListView, DeleteView
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render
from djgentelella.models import MenuItem as DJMenuItem
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.contrib.staticfiles import finders
from django.core.files.base import File
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.loader import get_template, render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from xhtml2pdf import pisa
from async_notifications.utils import send_email_from_template
from matricula.forms import CategoryCreateForm, CategorySearchForm, \
    CourseSearchForm, CourseCreateForm, MenuItemSearchForm, \
    MenuItemCreateForm, PeriodCreateForm, PeriodSearchForm, GroupCreateForm, \
    GroupSearchForm, EnrollSearchForm, EnrollCreateForm, StudentSearchForm, \
    StudentAdminCreateForm, PageCreateForm, PageSearchForm, MenuItemAddForm, \
    PreEnrollAddGroupForm, GroupAddForm, GroupEditForm, PermissionForm
from matricula.models import Category, Course, Period, Group, \
    Enroll, Student, Page, Professor
from matricula.views.utils import get_expire_date
from .utils import get_active_period

MONTHS_DICT = {
    'January': 'enero',
    'February': 'febrero',
    'March': 'marzo',
    'April': 'abril',
    'May': 'mayo',
    'June': 'junio',
    'July': 'julio',
    'August': 'agosto',
    'September': 'setiembre',
    'October': 'octubre',
    'November': 'noviembre',
    'December': 'diciembre'
}


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


@method_decorator(permission_required('matricula.view_category'), name='dispatch')
class CategoryList(ListView):
    template_name = "categories/category_list.html"
    paginate_by = 30

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(CategoryList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = Category.objects.all()
        name = self.request.GET.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CategoryCreateForm()
        name = self.request.GET.get('name', None)
        if name is not None:
            context["form_search"] = CategorySearchForm(self.request.GET)
        else:
            context['form_search'] = CategorySearchForm()
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
            form.save()
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
    success_url = "/matricula/enrrolment/categories/"
    success_message = "Categoría eliminada con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(CategoryDelete, self).dispatch(*args, **kwargs)

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
                messages.success(request, "Categoría guardada con éxito")
                form.save()
                return HttpResponseRedirect(reverse('categories'))
            else:
                messages.error(request, "Error al actualizar")
        else:
            if request.method == "GET":
                category = Category.objects.get(pk=pk)
                form = CategoryCreateForm(category.__dict__)
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

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(CourseList, self).dispatch(*args, **kwargs)

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
        name = self.request.GET.get('name', None)
        if name is not None:
            context["form_search"] = CourseSearchForm(self.request.GET)
        else:
            context['form_search'] = CourseSearchForm()
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
    success_url = "/matricula/enrrolment/courses/"
    success_message = "Curso eliminada con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(CourseDelete, self).dispatch(*args, **kwargs)

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
        if request.method == "POST":
            course = Course.objects.get(pk=pk)
            form = GroupAddForm(request.POST)
            if form.is_valid():
                group = Group(
                    name=form.cleaned_data['name'],
                    period=get_active_period(),
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
                    flow=form.cleaned_data['flow']
                )
                group.save()
                messages.success(request, "Grupo agregado con éxito")
                return HttpResponseRedirect(reverse('enrrolment_courses'))
            else:
                messages.error(request, "Error al crear grupo")
                return render(request, 'courses/course_group_create.html', {'form': form})
        form = GroupAddForm()
        return render(request, 'courses/course_group_create.html', {'form': form})
    return HttpResponseRedirect(reverse('enrrolment_courses'))


@method_decorator(permission_required('djgentelella.view_menuitem'), name='dispatch')
class MenuItemList(ListView):
    template_name = "menuitems/menuitem_list.html"
    model = DJMenuItem
    paginate_by = 30

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(MenuItemList, self).dispatch(*args, **kwargs)

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
    success_url = "/matricula/enrrolment/menuitems"
    success_message = "Menú eliminado con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(MenuItemDelete, self).dispatch(*args, **kwargs)

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

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(PeriodList, self).dispatch(*args, **kwargs)

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
        return context


@permission_required('matricula.add_period')
def create_period(request):
    context = {}
    if request.method == 'POST':
        form = PeriodCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request, "Período guardado con éxito")
            return HttpResponseRedirect(reverse('periods'))
        else:
            messages.error(request, "Error al guardar el período")
            context['object_list'] = Period.objects.all()
            return render(request, 'periods/period_list.html', context)
    return HttpResponseRedirect(reverse('periods'))


@method_decorator(permission_required('matricula.delete_period'), name='dispatch')
class PeriodDelete(DeleteView):
    model = Period
    success_url = "/matricula/enrrolment/periods"
    success_message = "Período eliminado con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(PeriodDelete, self).dispatch(*args, **kwargs)

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
                messages.success(request, "Período guardado con éxito")
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

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(GroupList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        user = self.request.user
        professor = Professor.objects.filter(user=user).first()

        self.form = GroupSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['name']:
            queryset = queryset.filter(
                Q(name__icontains=self.form.cleaned_data['name'])|
                Q(course__name__icontains=self.form.cleaned_data['name'])|
                Q(course__category__name__icontains=self.form.cleaned_data['name']))
        if self.form.cleaned_data['course']:
            queryset = queryset.filter(
                course__in=self.form.cleaned_data['course'])
        if self.form.cleaned_data['period']:
            queryset = queryset.filter(period__in=self.form.cleaned_data['period'])
        if self.form.cleaned_data['currency']:
            queryset = queryset.filter(currency__in=self.form.cleaned_data['currency'])
        if self.form.cleaned_data['category']:
            queryset = queryset.filter(course__category__in=self.form.cleaned_data['category'])
        if self.form.cleaned_data['open'] and int(self.form.cleaned_data['open']) != GroupSearchForm.DO_NOT_APPLY:
            if int(self.form.cleaned_data['open']) == GroupSearchForm.OPEN:
                queryset = queryset.filter(is_open=True)
            else:
                queryset = queryset.filter(is_open=False)

        if not user.is_superuser:
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
                    enroll = Enroll.objects.filter(pk__in=form.cleaned_data['students'], group=group)
                    for instance in enroll:
                        instance.enroll_finished = True
                        instance.save()
                    messages.success(request, "Estudiantes inscritos con éxito")
                    return HttpResponseRedirect(reverse('pre_enroll_group', args=[pk]))
            messages.error(request, "Error al realizar la acción")
            return HttpResponseRedirect(reverse('pre_enroll_group', args=[pk]))
        else:
            if request.method == "GET":
                instance = Group.objects.get(pk=pk)
                context['object'] = instance
                context['pre_enroll_list'] = Enroll.objects.filter(group=instance, enroll_finished=False)
                return render(
                    request, 'groups/pre_enroll_group_list.html', context)
    return HttpResponseRedirect(reverse('periods'))


@permission_required('matricula.add_group')
def create_group(request):
    context = {}
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            group = Group(
                name=form.cleaned_data['name'],
                course=form.cleaned_data['course'],
                period=get_active_period(),
                schedule=form.cleaned_data['schedule'],
                pre_enroll_start=form.cleaned_data['pre_enroll_start'],
                pre_enroll_finish=form.cleaned_data['pre_enroll_finish'],
                enroll_start=form.cleaned_data['enroll_start'],
                enroll_finish=form.cleaned_data['enroll_finish'],
                is_paid=form.cleaned_data['is_paid'],
                currency=form.cleaned_data['currency'],
                cost=form.cleaned_data['cost'],
                maximum=form.cleaned_data['maximum'],
                flow=form.cleaned_data['flow']
            )
            group.save()
            messages.success(request, "Grupo guardado con éxito")
            return HttpResponseRedirect(reverse('groups_enroll'))
        else:
            messages.error(request, "Error al guardar grupo")
    else:
        context['form'] = GroupCreateForm()
    return render(request, 'groups/group_create.html', context)


@method_decorator(permission_required('matricula.delete_group'), name='dispatch')
class GroupDelete(DeleteView):
    model = Group
    success_url = "/matricula/enrrolment/groups"
    success_message = "Grupo eliminado con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(GroupDelete, self).dispatch(*args, **kwargs)

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
            if form.is_valid():
                messages.success(request, "Grupo guardado con éxito")
                form.save()
                return HttpResponseRedirect(reverse('groups_enroll'))
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
    writer = csv.writer(response)
    if pk is not None:
        group = Group.objects.get(pk=pk)
        enrolls = group.enroll_set.all()
        writer.writerow([
            'username',
            'firstname',
            'lastname',
            'email',
            "course1"])
        for enroll in enrolls:
            first_name = enroll.student.user.first_name if enroll.student.user.first_name != "" else "default"
            last_name = enroll.student.user.last_name if enroll.student.user.last_name != "" else "default"
            writer.writerow([
                enroll.student.user.username,
                first_name,
                last_name,
                enroll.student.user.email,
                group.name])
        return response
    return HttpResponseRedirect(reverse('groups_enroll'))


@permission_required('matricula.can_list_students_group')
def list_students_group(request, pk=None):
    context = {}
    show_buttons_certificates = False
    show_column_action = False
    if pk is not None:
        context = {}
        if request.method == "POST":
            group = Group.objects.get(pk=pk)
            if group:
                form = PreEnrollAddGroupForm(request.POST)
                if form.is_valid():
                    enroll = Enroll.objects.filter(pk__in=form.cleaned_data['students'])
                    for instance in enroll:
                        instance.enroll_finished = True
                        instance.save()
                    messages.success(request, "Estudiantes inscritos con éxito")
                    return HttpResponseRedirect(reverse('pre_enroll_group', args=[pk]))
            messages.error(request, "Error al realizar la acción")
            return HttpResponseRedirect(reverse('pre_enroll_group', args=[pk]))
        else:
            if request.method == "GET":
                instance = Group.objects.get(pk=pk)
                context['object'] = instance

                enroll_list = Enroll.objects.filter(group=instance)
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
                return render(
                    request, 'groups/group_students_list.html', context)
    return HttpResponseRedirect(reverse('periods'))


@permission_required('matricula.can_open_group')
def open_group(request, pk):
    try:
        group = Group.objects.get(pk=pk)
    except Exception:
        messages.error(_("Group Not Found"))
    enrolls = Enroll.objects.filter(group=group)
    enrolls.update(enroll_activate=True)
    if request.GET.get('sendemail', '0') == '1':
        send_email_from_template(
            'email_open_group',
            [enroll.student.user.email for enroll in enrolls],
            {
                "url": request.build_absolute_uri(
                    reverse('course', args=[group.course.pk])),
                "group": group,
            },
            enqueued=False,
            user=None)
    messages.success(request, "Grupo aperturado con éxito")
    return HttpResponseRedirect(reverse('list_students_group', args=[pk, ]))


@permission_required('matricula.can_close_group')
def close_group(request, pk):
    try:
        group = Group.objects.get(pk=pk)
    except Exception:
        messages.error(_("Group Not Found"))
    enrolls = Enroll.objects.filter(group=group)
    enrolls.update(enroll_activate=False)
    if request.GET.get('sendemail', '0') == '1':
        send_email_from_template(
            'email_close_group',
            [enroll.student.user.email for enroll in enrolls],
            {
                "url": request.build_absolute_uri(
                    reverse('courses')),
                "group": group,
            },
            enqueued=False,
            user=None)
    messages.success(request, "Grupo cerrado con éxito")
    return HttpResponseRedirect(reverse('list_students_group', args=[pk, ]))


@permission_required('matricula.can_view_pdf_enrolled_group')
def export_enrolled_group(request, pk=None):
    group = get_object_or_404(Group, pk=pk)
    attrs = {'group__pk': pk}
    if request.GET.get('finished', '0') == '1':
        attrs['enroll_finished'] = True
    elif request.GET.get('finished', '0') == '2':
        attrs['enroll_finished'] = False
    if request.GET.get('activate', '0') == '1':
        attrs['enroll_activate'] = True
    elif request.GET.get('activate', '0') == '2':
        attrs['enroll_activate'] = False
    student_list = Enroll.objects.filter(**attrs)
    template = get_template('Pdf/student_list.html')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    html = template.render({'student_list': student_list, 'group': group})
    pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
    if not pisa_status.err:
        return response
    return HttpResponse("Error " + str(pisa_status.err) + "  " + html)


@method_decorator(permission_required('matricula.view_enroll'), name='dispatch')
class EnrollList(ListView):
    template_name = "enrolls/enroll_list.html"
    model = Enroll
    paginate_by = 30

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(EnrollList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = EnrollSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['student']:
            queryset = queryset.filter(student__in=self.form.cleaned_data['student'])
        if self.form.cleaned_data['group']:
            queryset = queryset.filter(group__in=self.form.cleaned_data['group'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_search'] = EnrollSearchForm(self.request.GET)
        return context


@permission_required('matricula.add_enroll')
def create_enroll(request):
    context = {}
    if request.method == 'POST':
        form = EnrollCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request, "Matrícula guardada con éxito")
            return HttpResponseRedirect(reverse('enrolls'))
        else:
            messages.error(request, "Error al guardar matrícula")
    else:
        context['form'] = EnrollCreateForm()
    return render(request, 'enrolls/enroll_create.html', context)


@permission_required('matricula.change_enroll')
def edit_enroll(request, pk=None):
    if pk is not None:
        if request.method == "POST":
            instance = Enroll.objects.get(pk=pk)
            form = EnrollCreateForm(request.POST, instance=instance)
            if form.is_valid():
                messages.success(request, "Matrícula guardada con éxito")
                form.save()
                return HttpResponseRedirect(reverse('enrolls'))
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'enrolls/enroll_update.html', {'form': form})
        else:
            if request.method == "GET":
                instance = Enroll.objects.get(pk=pk)
                form = EnrollCreateForm(initial=instance.__dict__)
                return render(request, 'enrolls/enroll_update.html', {'form': form})
    return HttpResponseRedirect(reverse('enrolls'))


@method_decorator(permission_required('matricula.delete_enroll'), name='dispatch')
class EnrollDelete(DeleteView):
    model = Enroll
    success_url = "/matricula/enrrolment/enrolls"
    success_message = "Matrícula eliminada con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(EnrollDelete, self).dispatch(*args, **kwargs)

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

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(StudentList, self).dispatch(*args, **kwargs)

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
        return context


@permission_required('matricula.add_student')
def create_student(request):
    context = {}
    if request.method == 'POST':
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
                expired_at=get_expire_date())
            student.save()
            send_email_from_template(
                'set_email_first_academy', user.email,
                {
                    "url": request.build_absolute_uri(
                        reverse('recover_password')),
                    'student': student
                },
                enqueued=False,
                user=None)
            messages.success(request, "Estudiante guardada con éxito")
            return HttpResponseRedirect(reverse('students'))
        else:
            messages.error(request, "Error al guardar Estudiante")
    else:
        context['form'] = StudentAdminCreateForm()
    return render(request, 'students/student_create.html', context)


@permission_required('matricula.change_student')
def edit_student(request, pk=None):
    if pk is not None:
        if request.method == "POST":
            instance = User.objects.get(pk=pk)
            form = StudentAdminCreateForm(request.POST, instance=instance)
            if form.is_valid():
                messages.success(request, "Estudiante guardada con éxito")
                form.save()
                instance.student.organization = form.cleaned_data['organization']
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
                inst['organization'] = instance.student.organization
                form = StudentAdminCreateForm(initial=inst)
                return render(
                    request, 'students/student_update.html', {'form': form})
    return HttpResponseRedirect(reverse('students'))


@method_decorator(permission_required('matricula.delete_student'), name='dispatch')
class StudentDelete(DeleteView):
    model = Student
    success_url = "/matricula/enrrolment/students"
    success_message = "Estudiante eliminada con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(StudentDelete, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        student = self.get_object()
        user = User.objects.get(pk=student.user.pk)
        user.is_active = False
        user.save()
        messages.success(self.request, self.success_message)
        return super(StudentDelete, self).delete(request, *args, **kwargs)


@permission_required('matricula.can_recovery_pass_student')
def recovery_pass_student(request, pk=None):
    if (pk is not None):
        student = Student.objects.get(pk=pk)
        if student:
            send_email_from_template(
                'email_recovery_academy', student.user.email, {
                    'url': request.build_absolute_uri(
                        reverse('recover_password')),
                    'user': student.user,
                    'student': student
                },
                enqueued=False,
                user=None)
            messages.success(
                request, "Se ha enviado correo de recuperación de contraseña.")
        else:
            messages.error(request, "El usuario no fue encontrado")
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
                Q(slug__icontains=self.form.cleaned_data['slug'])| 
                Q(title__icontains=self.form.cleaned_data['slug']))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_search'] = PageSearchForm(self.request.GET)
        pages = []
        for page in self.get_queryset():
            page.menu = DJMenuItem.objects.filter(
                url_name="/pages/" + page.slug).first()
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
                    url_name='/pages/' + page.slug,
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
                    url_name='/pages/' + page.slug,
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
    success_url = "/matricula/enrrolment/pages"
    success_message = "Página eliminada con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(PageDelete, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        page = self.get_object()
        DJMenuItem.objects.filter(url_name="/pages/"+page.slug).all().delete()
        messages.success(self.request, self.success_message)
        return super(PageDelete, self).delete(request, *args, **kwargs)


@method_decorator(permission_required('matricula.delete_page'), name='dispatch')
class MenuPageDelete(DeleteView):
    model = DJMenuItem
    success_url = "/matricula/enrrolment/pages"
    success_message = "Menú eliminado con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(MenuPageDelete, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MenuPageDelete, self).delete(request, *args, **kwargs)


def build_pdf_certificate(enroll):
    html = 'certificate.html'
    month = MONTHS_DICT['{:%B}'.format(now())]
    date = str(now().day) + " de " + month + " del " + str(now().year)
    sourceHtml = render_to_string('certificate.html', context={
        'enroll': enroll,
        'certificate_date': date
    })
    # FIXME the variable 'enqueued' == False, it must be false o we should change it to True?!
    resultFile = io.BytesIO()

    pisaStatus = pisa.CreatePDF(
        sourceHtml,  # the HTML to convert
        dest=resultFile,  # file handle to recieve result
        link_callback=link_callback)
    if pisaStatus.err:
        return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisaStatus.err,
                                                                               html))
    resultFile.seek(0)
    file_name = f'certificado_{str(enroll.group)}_{str(enroll.student)}.pdf'
    enroll.pdf_certificate = File(resultFile, name=file_name)
    enroll.save()

@staff_member_required
def build_pdf_certificate_view(request, pk):
    enroll = get_object_or_404(Enroll, pk=pk)
    build_pdf_certificate(enroll)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="'+str(enroll.group)+"-"+str(enroll.student)+'.pdf"'
    response.write(enroll.pdf_certificate.read())
    return response

@staff_member_required
def regenerate_certificate(request, pk_group, pk):
    enroll = get_object_or_404(Enroll, pk=pk)
    build_pdf_certificate(enroll)
    messages.success(request, "Certificado regenerado con éxito.")
    return redirect('list_students_group', pk=pk_group)


def build_pdf_certificate_list(request, pk):

    enroll_list = Enroll.objects.filter(group__pk=pk, course_status="approved", enroll_finished=True)
    if enroll_list:
        for enroll in enroll_list:
            if enroll.pdf_certificate is None or enroll.pdf_certificate == "":
                build_pdf_certificate_view(request, enroll.pk)
        messages.success(request, "Certificados generados exitosamente.")
        return redirect("list_students_group", pk=pk)