# encoding: utf-8
'''
Created on 18/10/2020

@author: allexiusw
'''
from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404
from matricula.models import Category
from matricula.forms import CategoryCreateForm, CategorySearchForm


class CategoryList(ListView):
    template_name = "categories/category_list.html"

    def get_queryset(self):
        queryset = Category.objects.all()
        name = self.request.GET.get('name', None)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CategoryCreateForm()
        if self.request.GET:
            context["form_search"] = CategorySearchForm(self.request.GET)
        else:
            context['form_search'] = CategorySearchForm()
        return context
    
    
    