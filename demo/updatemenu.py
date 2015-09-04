'''
Created on 3/9/2015

@author: luisza
'''

from matricula.models import MenuItem

def update():
    menu = MenuItem.objects.create(
            name='demo',
            type=2,
            description="about",
            order=1)

    menu = MenuItem.objects.create(
            name='feature',
            type=2,
            description="features",
            order=1)