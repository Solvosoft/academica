# encoding: utf-8
'''
Created on 18/10/2020

@author: allexiusw
'''
from django.views.generic import ListView, DeleteView
from django.shortcuts import render, get_object_or_404
from matricula.models import Category, Course
from matricula.forms import CategoryCreateForm, CategorySearchForm,\
    CourseSearchForm, CourseCreateForm
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
            messages.success(request, "Registro creado con exíto!")
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
    success_message = "Categoría eliminada con exíto"

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
                messages.success(request, "Categoría guardada con exíto")
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
            messages.success(request, "Curso guardado con exíto")
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
    success_message = "Curso eliminada con exíto"

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
                messages.success(request, "Curso guardado con exíto")
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
