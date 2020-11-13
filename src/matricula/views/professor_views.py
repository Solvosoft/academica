from django.shortcuts import render

from matricula.forms import ProfessorEditForm
from matricula.models import Professor

def edit_professor(request):

    user = request.user
    professor = Professor.objects.filter(user=user).first()

    form = ProfessorEditForm(initial={
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'personal_description': professor.personal_description
    })

    context = {'form': form}

    return render(request, "professor/edit.html", context=context)