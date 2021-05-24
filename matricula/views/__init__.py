from django.shortcuts import redirect
from django.urls import reverse
from matricula.models import MenuItem


def index(request):
    index = MenuItem.objects.filter(is_index=True)
    if index:
        index = index[0]
        if index.type == 1:
            return redirect(reverse("academica_pages", args=(index.name,)))
        elif index.type == 2:
            return redirect(reverse(index.name, args=(index.description,)))
        else:
            return redirect(reverse(index.name))
    return redirect(reverse('courses'))
