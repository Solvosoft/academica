# encoding: utf-8
'''
Created on 17/5/2015

@author: luisza
'''
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from matricula.forms import StudentCreateForm
from matricula.models import Student, Enroll
from django.core.mail import send_mail
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib import auth
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.views.generic.edit import UpdateView


def create_user(request):
    if request.method == 'POST':
        form = StudentCreateForm(request.POST)
        if form.is_valid():
            user = Student.objects.create_user(form.cleaned_data['name'],
                                               form.cleaned_data['email'],
                                               form.cleaned_data['password'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            mail_body = render_to_string("email_confirmation.html",
                     {
                      "url": request.build_absolute_uri(reverse('confirm_email')),
                      "user": user,
                      })
            send_mail(_('Email confirmation'),
                      'Url confirmation %s?id=%d&key=%s' % (request.build_absolute_uri(reverse('confirm_email')),
                                               user.pk,
                                               user.confirmation_key
                                               ),
                      settings.DEFAULT_FROM_EMAIL, [form.cleaned_data['email']],
                      html_message=mail_body)
            return render(request, 'messages.html',
                          {'message': _('Thank you, We will send you an email soon'),
                           'mtype': 'success'}
                          )
    else:
        form = StudentCreateForm()
    if request.user.is_authenticated and not request.user.is_staff:
        messages.info(request, _('Your user have not permission for see this page'))
        return redirect(reverse('index'))

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

@ajax
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
        return {
        'inner-fragments': {
            '#message': '<div class="alert alert-danger"  role="alert">' + str(_('Login failed')) + '</div>'
            },
                }

    return redirect(reverse('index'))


@login_required
def logout(request):
    '''
        Realiza el cierre de sesión del usuario que se encuentra logueado, redirecciona a la página inicial
        del sistema (la de autenticación)
    '''
    auth.logout(request)
    return redirect(reverse('index'))


def login(request):
    return render(request, 'login.html')


def recover_password(request):
    new_pass = None
    message = None
    form_message = ''
    if request.method == 'GET':
        key = request.GET.get('key', '')
        id = request.GET.get('id', -1)
    else:
        key = request.POST.get('key', '')
        id = request.POST.get('id', -1)
        new_pass = request.POST.get('password', '')

    user = get_object_or_404(Student, pk=id)
    if user.confirmation_key == key:
        if new_pass:
            user.set_password(new_pass)
            user.save()
            message = _("Password changed")
            form_message = "success"
        if not new_pass and request.method == 'POST':
            message = _("Wrong password")
            form_message = "warning"

        return render(request, 'recover_password.html', {'user': user, 'change': 'form',
                                                         'message': message,
                                                         'form_message': form_message})
    else:
        return render(request, 'recover_password.html', {'user': user, 'change': 'error',
                                                         'message': _("Wrong confirmation key") 
                                                         })


@ajax
def mail_recover_pass(request):
    email = request.POST.get('email', 'no-email')
    user = Student.objects.filter(email=email)
    if user.exists():
        user = user[0]
        mail_body = render_to_string("email_recovery.html",
                {
                 'url': request.build_absolute_uri(reverse('recover_password')),
                 'user': user,
                })
        send_mail(_('Password recovery'),
                      'Url for recover %s?id=%d&key=%s' % (request.build_absolute_uri(reverse('recover_password')),
                                               user.pk,
                                               user.confirmation_key
                                               ),
                      settings.DEFAULT_FROM_EMAIL, [user.email],
                      html_message=mail_body)
        recover_message_type = 'success'
        recover_message = _('You will recive a message soon, check your email')
    else:
        recover_message_type = 'warning'
        recover_message = _('User not found')

    return {'inner-fragments': {'#recover_pass': render_to_string('recover.html', context={'recover_message_type': recover_message_type,
                                 'recover_message': recover_message
                                 }, context_instance=RequestContext(request))
                        }
            }


def get_profile(request):
    return redirect(reverse('myprofile', kwargs={'pk': request.user.pk}))


class StudentEdit(UpdateView):
    model = Student
    fields = ['first_name', 'last_name', 'email']
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):

        context = UpdateView.get_context_data(self, **kwargs)
        enroll = Enroll.objects.filter(student=self.object).order_by('enroll_date')
        context['enroll'] = enroll.filter(enroll_activate=True, enroll_finished=True)
        context['pre_enroll'] = enroll.filter(enroll_activate=True, enroll_finished=False)
        return context


def login_user(request):

    if not request.user.is_anonymous and not request.user.is_staff:
        messages.info(request, _('Your user have not permission for see this page'))
        return redirect(reverse('index'))

    else:
        return render(request, 'student_login.html')