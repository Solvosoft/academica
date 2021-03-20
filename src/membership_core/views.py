# -*- coding: UTF8 -*-
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView, CreateView
from django.http.response import HttpResponseRedirect

from .forms import UserSearchForm, UserAddForm, GroupAddForm
from .dashboard import TopStats
from .models import Country

from async_notifications.utils import send_email_from_template

from matricula.models import Category, FakeGroup



def servicios_stats():
    for category in Category.objects.all():
        yield (category.name, category.course_set.count())


def country_stats():
    for country in Country.objects.all().order_by('name'):
        total = country.student_set.count()
        if total:
            yield (country.flag, country.name, total)


@login_required
def index(request):
    if request.user.has_perm('membership_manager.can_show_dashboard'):
        context = {'topstat': TopStats(),
                'vencimientoanual_url': reverse('vencimientoanual-list'),
                'pagoanual_url': reverse('pagoanual-list'),
                'countries': country_stats(),
                'servicios_stats': servicios_stats()
                }
        return render(request, 'dashboard.html', context=context)
    return redirect(reverse('courses'))


@method_decorator(permission_required('auth.view_user'), name='dispatch')
class UserListView(ListView):
    template_name = "user/user_list.html"
    paginate_by = 30
    model = User

    def get_queryset(self):
        self.form = UserSearchForm(self.request.GET)
        self.form.is_valid()
        queryset = super().get_queryset().order_by("-is_active", "first_name", "last_name")
        if self.form.cleaned_data['user']:
            queryset = queryset.filter(pk__in=self.form.cleaned_data['user'])
        if self.form.cleaned_data['fakegroup']:
            queryset = queryset.filter(groups__fakegroup__in=self.form.cleaned_data['fakegroup'])
        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['formsearch'] = UserSearchForm(self.request.GET)
        return context


@method_decorator(permission_required('auth.add_user'), name='dispatch')
class AddUser(CreateView):
    model = User
    form_class = UserAddForm
    success_url = reverse_lazy('user_list')
    template_name = "user/create.html"

    def send_email(self,  user):
        schema = self.request.scheme+"://"
        send_email_from_template(
            'new_user_created_membership', user.email, {
                'user': user,
                'domain': schema+self.request.get_host(),
            },
            enqueued=False,
            user=None)

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        self.send_email(self.object)
        messages.success(self.request, "Usuaria registrada con éxito")
        return response


@method_decorator(permission_required('auth.change_user'), name='dispatch')
class EditUser(UpdateView):
    model = User
    form_class = UserAddForm
    template_name = 'user/edit.html'
    success_url = reverse_lazy('user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = context['object']
        context['user'] = user.pk
        return context

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, "Usuaria actualizada con éxito")
        return super().form_valid(form)


@permission_required('auth.delete_user')
def delete_user(request, pk):
    user = User.objects.filter(pk=pk).first()

    if user:
        user.delete()
        messages.success(request, "Usuaria eliminada con éxito")
        return redirect('user_list')


@permission_required('auth.change_user')
def deactivate_user(request, pk):
    user = User.objects.filter(pk=pk).first()
    if user:
        user.is_active = False
        user.save()
        messages.success(request, "Usuaria desactivada con éxito")
        return redirect('user_list')


@permission_required('auth.view_group')
@permission_required('auth.add_group')
def groups_list(request):

    if request.method == "POST":
        form = GroupAddForm(request.POST)
        if form.is_valid():
            group = form.save()
            FakeGroup.objects.create(group=group, name=group.name)
            messages.success(request, "Grupo registrado con éxito")
            return redirect('groups_list')
    else:
        form = GroupAddForm()

    groups_list = Group.objects.all()

    return render(request, "groups/groups_list.html", context={'form': form, 'group_edit': 0,
                                                                   'groups_list': groups_list})


@method_decorator(permission_required('auth.change_group'), name='dispatch')
class EditGroup(UpdateView):
    model = Group
    form_class = GroupAddForm
    template_name = 'groups/groups_list.html'
    success_url = reverse_lazy('groups_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group_edit'] = 1
        context['groups_list'] = Group.objects.all()
        group = Group.objects.get(pk=self.kwargs['pk'])
        context['form'] = GroupAddForm(instance=group, initial={'name':group.fakegroup.name})
        return context

    def form_valid(self, form):
        group = form.save(commit=False)
        fakegroup = FakeGroup.objects.get(group=group)
        fakegroup.name = group.name
        fakegroup.save()
        users = User.objects.filter(groups__in=[group])
        if users:
            for user in users:
                user.user_permissions.add(*group.permissions.all())
        messages.success(self.request, "Grupo actualizado con éxito")
        return HttpResponseRedirect(self.success_url)


@permission_required('auth.delete_group')
def delete_group(request, pk):
    group = Group.objects.filter(pk=pk).first()

    if group:
        for user in User.objects.all():
            if group in user.groups.all():
                user.groups.remove(group)

        object_pk = group.pk
        object_repr = str(group)
        group.delete()
        messages.success(request, "Grupo eliminado con éxito")
        return redirect('groups_list')
