from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from matricula.models import MenuItem


def index(request):
    index = MenuItem.objects.filter(is_index=True)
    if index:
        index = index[0]
        if index.type == 1:
            return redirect(reverse("academica_pages", args=(index.name,)))
        else:
            return reverse(index.name)
    return redirect(reverse('courses'))
