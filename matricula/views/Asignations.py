'''
Created on 11/8/2015

@author: luisza
'''
from django.shortcuts import render

def asignations(request):
    return render(request, 'matricula/groupweek.html')