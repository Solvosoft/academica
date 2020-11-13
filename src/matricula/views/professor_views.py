from django.contrib import messages
from django.shortcuts import render, redirect

from matricula.forms import ProfessorEditForm
from matricula.models import Professor

def edit_professor(request):
    user = request.user
    professor = Professor.objects.filter(user=user).first()

    if request.method == "POST":

        print(request.POST)

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

    return render(request, "professor/edit.html", context=context)