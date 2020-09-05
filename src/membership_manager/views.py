from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from membership_manager.models import Contact, Organization
from djgentelella.cruds.base import CRUDView


@login_required
def index(request):
    return render(request, 'membresias/home.html')


class ContactView(CRUDView):
    model = Contact
    template_name_base = "membresias/djgentelella/cruds"


class OrganizationView(CRUDView):
    model = Organization
    template_name_base = "membresias/djgentelella/cruds"