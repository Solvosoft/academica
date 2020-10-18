# encoding: utf-8
'''
Created on 18/10/2020

@author: allexiusw
'''
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from matricula.models import Category
from matricula.forms import CategoryCreateForm, CategorySearchForm
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect


class CategoryList(ListView):
    template_name = "categories/category_list.html"

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