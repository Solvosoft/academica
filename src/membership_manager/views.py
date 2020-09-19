from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from membership_manager.dashboard import TopStats
from membership_manager.models import Contact, Organization, Membership
from djgentelella.cruds.base import CRUDView
from django.views.generic import ListView
from django.db.models import Q
from django.db.models.functions import Concat
from django.db.models import Value
import datetime


@login_required
def index(request):
    context = {'topstat': TopStats()}
    return render(request, 'membership/home.html', context=context)


class OrganizationView(CRUDView):
    model = Organization
    template_name_base = "membership/djgentelella/cruds"


class MembershipListView(ListView):
    template_name = "membership/membership_list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Membership.objects.all()
        q = self.request.GET.get('q')
        if(q is not None):
            # need to implement other filters
            queryset = Membership.objects.filter(
                    Q(contact__country__name__icontains=q) |
                    Q(organization__country__name__icontains=q) |
                    Q(organization__name__icontains=q) |
                    Q(contact__first_name__icontains=q) |
                    Q(contact__last_name__icontains=q)
                    )
        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['today'] = datetime.datetime.now
        return context


class ContactListView(ListView):
    template_name = "contact/contact_list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = Contact.objects.all()
        q = self.request.GET.get('q')
        if(q is not None):
            queryset = queryset.annotate(fullname=Concat(
                'first_name', Value(' '), 'last_name'))
            queryset = queryset.filter(
                Q(email__icontains=q) | Q(fullname__icontains=q))
        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context
