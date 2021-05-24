# encoding: utf-8
'''
Created on 17/5/2015

@author: luisza
'''
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from matricula.forms import StudentCreateForm, StudentEditForm
from matricula.models import Student, Enroll
from django.core.mail import send_mail
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib import auth
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django_ajax.decorators import ajax
from django.template.loader import render_to_string
from django.template.context import RequestContext
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.timezone import now


def create_user(request):
    if request.method == 'POST':
        form = StudentCreateForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['name'],
                                               form.cleaned_data['email'],
                                               form.cleaned_data['password'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.is_active = False
            user.save()
            student = Student(user=user)
            student.save()
            mail_body = render_to_string("email_confirmation.html",
                     {
                      "url": request.build_absolute_uri(reverse('confirm_email')),
                      "user": user,
                      'email': user.email,
                      'student': student
                      })
            send_mail(_('Email confirmation'),
                      'Url confirmation %s?id=%d&key=%s' % (request.build_absolute_uri(reverse('confirm_email')),
                                                student.pk,
                                                str(student.key)
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
        return redirect(reverse('courses'))

    return render(request, 'student_create.html', {'form': form})


@login_required
def add_student(request):
    if request.method == 'POST':
        if not hasattr(request.user, "student"):
            student = Student(user=request.user, confirmed_at=now())
            student.save()
            mail_body = render_to_string("email_welcome.html",
                     {
                      "url": request.build_absolute_uri(reverse('courses')),
                      "user": request.user,
                      })
            send_mail(_('Email confirmation'),
                      'Url confirmation %s' % (request.build_absolute_uri(reverse('courses'))),
                      settings.DEFAULT_FROM_EMAIL, [request.user.email],
                      html_message=mail_body)
            messages.success(request,_('Thank you, We will send you an email soon'))
            return redirect(reverse('courses'))
        else:
            return redirect(reverse('courses'))
    return render(request, 'student_add.html')


def confirm_email(request):
    id = request.GET.get('id', -1)
    key = request.GET.get('key', '')

    try:
        student = Student.objects.get(pk=id)
    except:
        return render(request, 'messages.html',
                          {'message': _('Key not found'),
                           'mtype': 'warning'}
                          )
    try:
        student.confirm(key)
        if student.user.is_active:
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
    if user is not None and user.is_active:
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

    return redirect(reverse('courses'))


@login_required
def logout(request):
    '''
        Realiza el cierre de sesión del usuario que se encuentra logueado, redirecciona a la página inicial
        del sistema (la de autenticación)
    '''
    auth.logout(request)
    return redirect(reverse('courses'))


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
    student = get_object_or_404(Student, pk=id)
    if str(student.key) == str(key):
        if new_pass:
            student.user.set_password(new_pass)
            student.save()
            student.user.save()
            return render(request, 'messages.html',
                          {'message': "La contraseña ha sido cambiada con éxito.",
                           'mtype': 'success'}
                          )
        if not new_pass and request.method == 'POST':
            messages.error(request, _("Wrong password"))
        return render(request, 'recover_password.html', {'student': student, 'change': 'form',
                                                         'message': message,
                                                         'form_message': form_message})
    else:
        return render(request, 'recover_password.html', {'student': student, 'change': 'error',
                                                         'message': _("Wrong confirmation key") 
                                                         })


@ajax
def mail_recover_pass(request):
    email = request.POST.get('email', 'no-email')
    students = Student.objects.filter(user__email__exact=email)
    if students:
        student = students[0] 
        mail_body = render_to_string("email_recovery.html",
                {
                 'url': request.build_absolute_uri(reverse('recover_password')),
                 'user': student.user,
                 'student': student
                })
        send_mail(_('Password recovery'),
                      'Url for recover %s?id=%d&key=%s' % (request.build_absolute_uri(reverse('recover_password')),
                                               student.user.pk,
                                               student.key
                                               ),
                      settings.DEFAULT_FROM_EMAIL, [student.user.email],
                      html_message=mail_body)
        recover_message_type = 'success'
        recover_message = _('You will recive a message soon, check your email')
    else:
        recover_message_type = 'warning'
        recover_message = _('User not found')

    return {'inner-fragments': {'#recover_pass': render_to_string('recover.html', context={'recover_message_type': recover_message_type,
                                'recover_message': recover_message})
                        }
            }

@login_required
def get_profile(request):
    return redirect(reverse('myprofile', kwargs={'pk': request.user.pk}))


@method_decorator(login_required, name='dispatch')
class StudentEdit(SuccessMessageMixin, UpdateView):
    model = User
    form_class = StudentEditForm
    template_name = "matricula/student_form.html"
    success_message = "Perfil actualizado con exíto"

    def get_context_data(self, **kwargs):
        context = UpdateView.get_context_data(self, **kwargs)
        enroll = Enroll.objects.filter(student__user=self.object).order_by('enroll_date')
        context['enroll'] = enroll.filter(enroll_activate=True, enroll_finished=True)
        context['pre_enroll'] = enroll.filter(enroll_activate=True, enroll_finished=False)
        return context

    def get_success_url(self):
        pk=self.kwargs['pk']
        return reverse_lazy('myprofile', kwargs={'pk': pk}) 

    def get(self, request, *args, **kwargs):
        # self.object = self.get_object()
        if not hasattr(self.request.user, 'student'):
            return redirect(reverse('courses'))
        else:
            return super(StudentEdit, self).get(request,*args, **kwargs)
    
    def get_object(self):
        return self.request.user


def login_user(request):
    if not request.user.is_anonymous and not request.user.is_staff:
        messages.info(request, _('Your user have not permission for see this page'))
        return redirect(reverse('courses'))

    else:
        return render(request, 'student_login.html')