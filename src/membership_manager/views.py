from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from membership_manager.models import Contact, Organization, Membership
from djgentelella.cruds.base import CRUDView
from django.views.generic import ListView
from django.db.models import Q


@login_required
def index(request):
    return render(request, 'membership/home.html')


class ContactView(CRUDView):
    model = Contact
    template_name_base = "membership/djgentelella/cruds"


class OrganizationView(CRUDView):
    model = Organization
    template_name_base = "membership/djgentelella/cruds"


class MembershipListView(ListView):
    template_name = "membership/membership_list.html"
    paginate_by = 8

    def get_queryset(self):
        queryset = Membership.objects.all()
        q = self.request.GET.get('q')
        if(q is not None):
            # need to implement countries filter but it will be overwrite soon
            queryset = Membership.objects.filter(
                    # Q(contact__country__in=q) |
                    Q(organization__name__icontains=q) |
                    Q(contact__first_name__icontains=q) |
                    Q(contact__last_name__icontains=q)
                    )
        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the publisher
        context['q'] = self.request.GET.get('q', '')
        return context
