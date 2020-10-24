from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView, CreateView

from membership_manager.forms import UserSearchForm, UserAddForm, GroupAddForm
from membership_manager.utils import add_logentry


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
        if self.form.cleaned_data['group']:
            queryset = queryset.filter(groups__in=self.form.cleaned_data['group'])
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
        schema=self.request.scheme+"://"
        context = {
            'user': user,
            'domain': schema+self.request.get_host(),
        }
        send_mail(subject="Nueva usuaria creada en la plataforma",
                  message="Por favor use un visor de html",
                  recipient_list=[user.email],
                  from_email=settings.DEFAULT_FROM_EMAIL,
                  html_message=render_to_string(
                      'gentelella/registration/new_user.html',
                      context=context
                  )
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        add_logentry("auth", "user", user.pk, str(user), self.request.user, 1)
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
        add_logentry("auth", "user", user.pk, str(user), self.request.user, 2)
        messages.success(self.request, "Usuaria actualizada con éxito")
        return super().form_valid(form)


@permission_required('auth.delete_user')
def delete_user(request, pk):
    user = User.objects.filter(pk=pk).first()

    if user:
        object_repr = str(user)
        object_pk = user.pk
        user.delete()
        add_logentry("auth", "user", object_pk, object_repr, request.user, 3)
        messages.success(request, "Usuaria eliminada con éxito")
        return redirect('user_list')


@permission_required('auth.change_user')
def deactivate_user(request, pk):
    user = User.objects.filter(pk=pk).first()
    if user:
        user.is_active = False
        user.save()
        add_logentry("auth", "user", user.pk, str(user), request.user, 2)
        messages.success(request, "Usuaria desactivada con éxito")
        return redirect('user_list')


@permission_required('auth.view_group')
@permission_required('auth.add_group')
def groups_list(request):

    if request.method == "POST":
        form = GroupAddForm(request.POST)

        if form.is_valid():
            group = form.save()
            add_logentry("auth", "group", group.pk, group.name, request.user, 1)
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
        return context

    def form_valid(self, form):
        group = form.save()
        add_logentry("auth", "group", group.pk, group.name, self.request.user, 2)
        messages.success(self.request, "Grupo actualizado con éxito")
        return super().form_valid(form)


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
        add_logentry("auth", "group", object_pk, object_repr, request.user, 3)

        messages.success(request, "Grupo eliminado con éxito")
        return redirect('groups_list')