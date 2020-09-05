from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from membership_manager.models import Contact, Organization, Membership
from djgentelella.cruds.base import CRUDView
from django.views.generic import ListView


@login_required
def index(request):
    return render(request, 'membresias/home.html')


class ContactView(CRUDView):
    model = Contact
    template_name_base = "membresias/djgentelella/cruds"


class OrganizationView(CRUDView):
    model = Organization
    template_name_base = "membresias/djgentelella/cruds"


class MembershipListView(ListView):
    model = Membership
