from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView

from matricula.decorators import user_group_perms
from matricula.forms import ProfessorEditForm, ProfessorSearchForm, ProfessorAddForm
from matricula.models import Professor

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
        context['formsearch'] = ProfessorSearchForm()
        return context


@method_decorator(permission_required('matricula.add_professor'), name='dispatch')
class CreateProfessor(CreateView):

    model = Professor
    form_class = ProfessorAddForm
    template_name = "professor/create.html"
    success_url = reverse_lazy("professors_list")

    def form_valid(self, form):
        instance = form.save()
        professor_group = Group.objects.filter(name="Profesores").first()
        instance.user.groups.add(professor_group)
        messages.success(self.request, "Profesora registrada exitosamente.")
        return super().form_valid(form)


@method_decorator(permission_required('matricula.change_professor'), name='dispatch')
class EditProfessor(UpdateView):

    model = Professor
    form_class = ProfessorAddForm
    template_name = "professor/edit.html"
    success_url = reverse_lazy("professors_list")

    def form_valid(self, form):
        self.object.save()
        messages.success(self.request, "Datos actualizados exitosamente.")
        return super().form_valid(form)


@permission_required('matricula.delete_professor')
def delete_professor(request, pk):
    professor = Professor.objects.filter(pk=pk).first()

    if professor:
        professor.delete()
        messages.success(request, "Profesora eliminada con éxito")
        return redirect('professors_list')


@permission_required('matricula.change_professor')
def deactivate_professor(request, pk):
    professor = Professor.objects.filter(pk=pk).first()

    if professor:
        professor.active = False
        professor.save()
        messages.success(request, "Profesora desactivada con éxito")
        return redirect('professors_list')