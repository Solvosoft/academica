# encoding: utf-8
'''
Created on 18/10/2020

@author: allexiusw
'''
from django.views.generic import ListView, DeleteView
from django.shortcuts import render, get_object_or_404
from matricula.models import Category, Course, MenuItem, Period, Group
from matricula.forms import CategoryCreateForm, CategorySearchForm,\
    CourseSearchForm, CourseCreateForm, MenuItemSearchForm,\
    MenuItemCreateForm, PeriodCreateForm, PeriodSearchForm, GroupCreateForm, GroupSearchForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.db.models import Q


@method_decorator(permission_required('matricula.view_category'), name='dispatch')
class CategoryList(ListView):
    template_name = "categories/category_list.html"

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


@permission_required('matricula.view_category')
def show_category(request, pk=None):
    context = {}
    if pk is not None:
        category = Category.objects.get(pk=pk)
        return render(request, 'categories/category_show.html', {
                                'object': category,})
    return HttpResponseRedirect(reverse(request, 'categories'))


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
    context = {}
    categories = Category.objects.all()
    search_form = CategorySearchForm()
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
                                    'object_list': categories,
                                    'form_search': search_form
                                    })
    return HttpResponseRedirect(reverse(request, 'categories'))


@method_decorator(permission_required('matricula.view_course'), name='dispatch')
class CourseList(ListView):
    template_name = "courses/course_list.html"
    model = Course

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(CourseList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = Course.objects.all()
        name = self.request.GET.get('name', None)
        if name is not None:
            queryset = queryset.filter(Q(name__icontains=name) | Q(content__icontains=name))
        category = self.request.GET.get('category', None)
        if category is not None:
             queryset = queryset.filter(Q(category__in=category))
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


@permission_required('matricula.view_course')
def show_course(request, pk=None):
    context = {}
    if pk is not None:
        course = Course.objects.get(pk=pk)
        return render(request, 'courses/course_show.html', {
                                'object': course,})
    return HttpResponseRedirect(reverse(request, 'enrrolment_courses'))


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
    context = {}
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


@method_decorator(permission_required('matricula.view_menuitem'), name='dispatch')
class MenuItemList(ListView):
    template_name = "menuitems/menuitem_list.html"
    model = MenuItem

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(MenuItemList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = MenuItemSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['name']:
           queryset = queryset.filter(
                Q(name__icontains=self.form.cleaned_data['name']) | 
                Q(description__icontains=self.form.cleaned_data['name']))
        if self.form.cleaned_data['parent']:
            queryset = queryset.filter(parent__in=self.form.cleaned_data['parent'])
        if self.form.cleaned_data['type']:
            queryset = queryset.filter(type__in=self.form.cleaned_data['type'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_search'] = MenuItemSearchForm(self.request.GET)
        return context


@permission_required('matricula.add_menuitem')
def create_menuitem(request):
    context = {}
    if request.method == 'POST':
        form = MenuItemCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request, "Elemento del menú guardado con éxito")
            return HttpResponseRedirect(reverse('menuitems'))
        else:
            messages.error(request, "Error al guardar elemento del menú")
    else:
        context['form'] = MenuItemCreateForm()
    return render(request, 'menuitems/menuitem_create.html', context)


@method_decorator(permission_required('matricula.delete_menuitem'), name='dispatch')
class MenuItemDelete(DeleteView):
    model = MenuItem
    success_url = "/matricula/enrrolment/menuitems"
    success_message = "Menú eliminado con éxito"

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(MenuItemDelete, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super(MenuItemDelete, self).delete(request, *args, **kwargs)


@permission_required('matricula.change_menuitem')
def edit_menuitem(request, pk=None):
    context = {}
    if pk is not None:
        if request.method == "POST":
            instance = MenuItem.objects.get(pk=pk)
            form = MenuItemCreateForm(request.POST, instance=instance)
            if form.is_valid():
                messages.success(request, "Elemento del menú guardado con éxito")
                form.save()
                return HttpResponseRedirect(reverse('menuitems'))
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'menuitems/menuitem_update.html', {'form': form})
        else:
            if request.method == "GET":
                instance = MenuItem.objects.get(pk=pk)
                form = MenuItemCreateForm(initial=instance.__dict__)
                return render(request, 'menuitems/menuitem_update.html', {'form': form})
    return HttpResponseRedirect(reverse('menuitems'))


@method_decorator(permission_required('matricula.view_period'), name='dispatch')
class PeriodList(ListView):
    template_name = "periods/period_list.html"
    model = Period

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
    success_url = "/matricula/enrrolment/periods"
    success_message = "Periodo eliminado con éxito"

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
                context['object_list'] = Period.objects.all()
                context['form'] = PeriodCreateForm(initial=instance.__dict__)
                context['form_search'] = PeriodSearchForm()
                return render(request, 'periods/period_update.html', context)
    return HttpResponseRedirect(reverse('periods'))


@method_decorator(permission_required('matricula.view_group'), name='dispatch')
class GroupList(ListView):
    template_name = "groups/group_list.html"
    model = Group

    def dispatch(self, *args, **kwargs):
        """ Permission check for this class """
        return super(GroupList, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = GroupSearchForm(self.request.GET)
        self.form.is_valid()
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
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_search'] = GroupSearchForm(self.request.GET)
        return context


@permission_required('matricula.add_group')
def create_group(request):
    context = {}
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        context['form'] = form
        if form.is_valid():
            form.save()
            messages.success(request, "Grupo guardado con éxito")
            return HttpResponseRedirect(reverse('groups'))
        else:
            messages.error(request, "Error al guardar grupo")
    else:
        context['form'] = GroupCreateForm()
    return render(request, 'groups/group_create.html', context)


@method_decorator(permission_required('matricula.delete_group'), name='dispatch')
class GroupDelete(DeleteView):
    model = MenuItem
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
    context = {}
    if pk is not None:
        if request.method == "POST":
            instance = Group.objects.get(pk=pk)
            form = GroupCreateForm(request.POST, instance=instance)
            if form.is_valid():
                messages.success(request, "Grupo guardado con éxito")
                form.save()
                return HttpResponseRedirect(reverse('groups'))
            else:
                messages.error(request, "Error al actualizar")
                return render(request, 'groups/group_update.html', {'form': form})
        else:
            if request.method == "GET":
                instance = Group.objects.get(pk=pk)
                form = GroupCreateForm(initial=instance.__dict__)
                return render(request, 'groups/group_update.html', {'form': form})
    return HttpResponseRedirect(reverse('groups'))
