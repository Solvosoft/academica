from django.shortcuts import render, redirect, get_object_or_404
from matricula.forms import StudentCreateForm
from matricula.models import Student, Course
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.conf import settings
# Create your views here.
from django.utils.translation import ugettext_lazy as _
from django.contrib import auth
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required


def create_user(request):
    if request.method == 'POST':
        form = StudentCreateForm(request.POST)
        if form.is_valid():
            user = Student.objects.create_user(form.cleaned_data['name'],
                                               form.cleaned_data['email'],
                                               form.cleaned_data['password'])
            send_mail(_('Email confirmation'),
                      'Url confirmation %s?id=%d&key=%s' % (request.build_absolute_uri(reverse('confirm_email')),
                                               user.pk,
                                               user.confirmation_key
                                               ),
                      settings.DEFAULT_FROM_EMAIL, [form.cleaned_data['email']],
                      html_message='Use <a href="%s?id=%d&key=%s" > this link </a> to confirm your email' % (
                                                                      request.build_absolute_uri(reverse('confirm_email')),
                                                                      user.pk,
                                                                      user.confirmation_key))
            return render(request, 'messages.html',
                          {'message': _('Thank you, We will send you an email soon'),
                           'mtype': 'success'}
                          )
    else:
        form = StudentCreateForm()

    return render(request, 'student_create.html', {'form': form})


def confirm_email(request):
    id = request.GET.get('id', -1)
    key = request.GET.get('key', '')

    try:
        user = Student.objects.get(pk=int(id))
    except:
        return render(request, 'messages.html',
                          {'message': _('Key not found'),
                           'mtype': 'warning'}
                          )

    try:
        user.confirm_email(key)

        if user.is_confirmed:
            return render(request, 'messages.html',
                          {'message': _('Congratulations, now you can login'),
                           'mtype': 'success'}
                      )
    except:
        pass

    return render(request, 'messages.html',
                      {'message': _('Key not found'),
                       'mtype': 'warning'}
                      )

def authenticate(request):
    '''
        Realiza la autenticación de los usuarios, redirecciona a la página principal del sistema
        o a la página inidicada en el next (página que requiere login a la cuál quería ingresar un usuario
        no logueado a la que va a ser redireccionado al autenticarse correctamente)

        En caso de error devuelve un 0 que indica que la autenticación no fue realizada correctamente 
        el cual es atrapado al realizar la comprobación para mostrar el mensaje de error al usuario
    '''
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active and user.is_confirmed:
        auth.login(request, user)
        mnext = request.POST.get('next', '')
        if mnext:
            return HttpResponse(mnext)
    else:
        return render(request, 'messages.html',
                      {'message': _('Login failed'),
                       'mtype': 'warning'}
                      )
    return redirect(reverse('index'))


@login_required
def logout(request):
    '''
        Realiza el cierre de sesión del usuario que se encuentra logueado, redirecciona a la página inicial
        del sistema (la de autenticación)
    '''
    auth.logout(request)
    return redirect(reverse('index'))


def courses(request):
    courses = Course.objects.all()
    user_auth = request.user.is_authenticated()
    return render(request, 'courses.html', {'courses': courses,
                                            'user_auth': user_auth})


def course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    user_auth = request.user.is_authenticated()
    
    return render(request, 'course.html',
                        {'course': course,
                        'add_schedule':True,
                        'user_auth': user_auth})    
