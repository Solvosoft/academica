'''
Created on 1/8/2015

@author: luisza
'''

from django.views.generic import DetailView
from matricula.models import Page


class PageDetail(DetailView):
    model = Page
