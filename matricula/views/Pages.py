'''
Created on 1/8/2015

@author: luisza
'''

from django.views.generic import DetailView
from matricula.models import Page, MultilingualContent
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class PageDetail(DetailView):
    # context_object_name = 'obj'
    model = Page

    def get_context_data(self, **kwargs):
        context = super(PageDetail, self).get_context_data(**kwargs)
        content = MultilingualContent.objects.filter(page=context['object'],
                                                     language=self.request.LANGUAGE_CODE)
        if not content:
            content = MultilingualContent.objects.filter(page=context['object'],
                                                         language=settings.LANGUAGE_CODE)
        if not content:
            content = MultilingualContent.objects.filter(page=context['object'])
        if not content:
            content = [{'title': _("Sorry page not found"), 'content': "" }]
        if content:
            context['page'] = content[0]
        return context
