from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from membership_manager.models import Contact, Organization, Membership
from djgentelella.cruds.base import CRUDView
from django.views.generic import ListView
from django.db.models import Q


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
    template_name = "membresias/membership_list.html"
    paginate_by = 10
    model = Membership
    
    def get_context_data(self, **kwargs):
        queryset = Membership.objects.all()
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if( q != None):
            #need to implement countries filter but it will be overwrite soon
            queryset = Membership.objects.filter(
                    #Q(contact__country__in=q) | 
                    Q(organization__name__icontains=q) |
                    Q(contact__first_name__icontains=q) |
                    Q(contact__last_name__icontains=q)
                    )
        context['memberships'] = queryset
        context['q'] = ''
        if q != None:
            context["q"]=q
        return context
