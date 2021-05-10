from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import Group, User
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView
from django.conf import settings

from matricula.decorators import user_group_perms
from matricula.forms import ProfessorEditForm, ProfessorSearchForm, ProfessorAddForm, UserCreateForm, UserEditForm
from matricula.models import Professor

from async_notifications.utils import send_email_from_template
from matricula.views.utils import checking_user


@login_required
@user_group_perms(perm='matricula.change_profile')
def edit_profile(request):
    user = request.user
    professor = Professor.objects.filter(user=user).first()

    if request.method == "POST":

        form = ProfessorEditForm(request.POST)

        if form.is_valid():

            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()

            if professor:
                professor.email = form.cleaned_data['email_students']
                professor.description = form.cleaned_data['description']
                professor.save()
            messages.success(request, "Información actualizada exitosamente.")
            return redirect('courses')
    else:
        form = ProfessorEditForm(initial={
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'email_students': professor.email,
            'description': professor.description
        })

    context = {'form': form}

    return render(request, "professor/personal_information.html", context=context)


@method_decorator(permission_required('matricula.view_professor'), name='dispatch')
class ProfessorsList(ListView):

    model = Professor
    paginate_by = 30
    template_name = "professor/professors_list.html"
    ordering = ["-active", "user__first_name"]

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['formsearch'] = ProfessorSearchForm(self.request.GET)
        context['has_data'] = Professor.objects.exists()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.form = ProfessorSearchForm(self.request.GET)
        self.form.is_valid()
        if self.form.cleaned_data['professor']:
            queryset = queryset.filter(pk__in=self.form.cleaned_data['professor'])
        if self.form.cleaned_data['status']:
            queryset = queryset.filter(active=self.form.cleaned_data['status'])
        return queryset


@method_decorator(permission_required('matricula.add_professor'), name='dispatch')
class CreateProfessor(CreateView):

    model = Professor
    form_class = ProfessorAddForm
    template_name = "professor/create.html"
    success_url = reverse_lazy("professors_list")
    
    def post(self, request, *args, **kwargs):
        context = {}
        form = ProfessorAddForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            professor_group = Group.objects.filter(name=settings.PROFESSOR_GROUP_NAME).first()
            instance.user.groups.add(professor_group)
            instance.user.user_permissions.add(*professor_group.permissions.all())
            instance.save()
            self.send_email(instance.user)
            messages.success(self.request, "Facilitadore registrade exitosamente.")
            return redirect(reverse('professors_list'))
        else:
            self.object = None
            context['form'] = form
            messages.error(self.request, "Error al guardar los datos.")
            return render(request, self.template_name, self.get_context_data(**kwargs))

    def send_email(self,  user):
        schema = self.request.scheme+"://"
        send_email_from_template(
        'new_professor_created_academy', user.email,
        {
            "url": self.request.build_absolute_uri(reverse('login')),
            'domain': schema+self.request.get_host(),
            "user": user,
            'professor': user.professor
        },
        enqueued=False,
        user=None)

def change_state_user(professor):
    professor.user.is_active = True
    if not professor.active:
        professor.user.is_active = False
    professor.user.save()

@method_decorator(permission_required('matricula.change_professor'), name='dispatch')
class EditProfessor(UpdateView):

    model = Professor
    form_class = ProfessorEditForm
    template_name = "professor/edit.html"
    success_url = reverse_lazy("professors_list")

    def post(self, request, *args, **kwargs):
        context = {}
        form = ProfessorEditForm(request.POST)
        user_form = UserEditForm(request.POST)
        if form.is_valid() and user_form.is_valid():
            professor = self.get_object()
            professor.user.first_name = user_form.cleaned_data['first_name']
            professor.user.last_name = user_form.cleaned_data['last_name']
            professor.user.email = user_form.cleaned_data['email']
            professor.user.save()
            professor.email = form.cleaned_data['email']
            professor.description = form.cleaned_data['description']
            professor.active = form.cleaned_data['active']
            professor.save()
            if not checking_user(professor.user):
                change_state_user(professor)
            messages.success(self.request, "Facilitadore actualizade exitosamente.")
            return redirect(reverse('professors_list'))
        else: 
            context['form'] = form
            context['user_form'] = user_form
            messages.error(self.request, "Error al guardar los datos.")
            return render(request, self.template_name, self.get_context_data(**context))

    def get_context_data(self, **kwargs):
        context = {}
        if 'form' not in kwargs:
            context['form'] = self.get_form()
        self.object = self.get_object()
        if 'user_form' not in kwargs:
            context['user_form'] = UserEditForm(initial=self.object.user.__dict__)
        return context


@permission_required('matricula.delete_professor')
def delete_professor(request, pk):
    professor = Professor.objects.filter(pk=pk).first()

    if professor:
        is_admin = professor.user.groups.filter(name=settings.ADMIN_GROUP_NAME)
        is_student = hasattr(professor.user, 'student')
        if not is_admin.exists() and not is_student:
            professor.user.delete()
        professor.delete()
        messages.success(request, "Facilitadore eliminade con exitosamente.")
        return redirect('professors_list')


@permission_required('matricula.change_professor')
def deactivate_professor(request, pk):
    professor = Professor.objects.filter(pk=pk).first()

    if professor:
        professor.active = False
        professor.save()
        messages.success(request, "Facilitadore desactivade con exitosamente.")
        return redirect('professors_list')


@method_decorator(permission_required('auth.add_user'), name='dispatch')
class AddUser(CreateView):
    model = User
    form_class = UserCreateForm
    success_url = reverse_lazy('create_simple_user')
    template_name = "user/create.html"

    def send_email(self,  user):
        schema = self.request.scheme+"://"
        send_email_from_template(
            'reset_password_academy', user.email, {
                'user': user,
                'domain': schema+self.request.get_host(),
            },
            enqueued=False,
            user=None)

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        self.send_email(self.object)
        messages.success(self.request, "Usuarie registrade con exitosamente.")
        return response
