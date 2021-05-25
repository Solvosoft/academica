# encoding: utf-8
'''
Created on 17/5/2015

@author: luisza
'''
import uuid

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.http.response import HttpResponse
from django.template.loader import render_to_string
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView

from django_ajax.decorators import ajax
from chunked_upload.models import ChunkedUpload
from async_notifications.utils import send_email_from_template

from matricula.models import Professor, Student, Enroll
from matricula.views.utils import get_expire_date
from matricula.forms import ProfessorEditProfileForm, StudentCreateForm,\
    StudentEditForm, UserEditForm, StudentResetPasswordForm


def create_user(request):
    if request.method == 'POST':
        form = StudentCreateForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                form.cleaned_data['name'], form.cleaned_data['email'],
                form.cleaned_data['password'])
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.is_active = False
            user.save()
            student = Student(
                user=user, organization=form.cleaned_data['organization'],
                country=form.cleaned_data['country'],
                phone_number=form.cleaned_data['phone_number'],
                expired_at=get_expire_date(),)
            student.save()
            schema = request.scheme+"://"
            send_email_from_template(
                'new_user_created_academy', user.email,
                {
                    "url": request.build_absolute_uri(reverse('confirm_email')),
                    'domain': schema+request.get_host(),
                    "user": user,
                    'student': student
                },
                enqueued=False,
                user=None)
            return render(
                request, 'messages.html', {
                    'message': _('Thank you, We will send you an email soon'),
                    'mtype': 'success'})
    else:
        form = StudentCreateForm()
    if request.user.is_authenticated and not request.user.is_staff:
        messages.info(
            request, _('Your user have not permission for see this page'))
        return redirect(reverse('courses'))
    return render(request, 'student_create.html', {'form': form})


@login_required
def add_student(request):
    if request.method == 'POST':
        if not hasattr(request.user, "student"):
            student = Student(
                user=request.user, confirmed_at=now(), expired_at=now())
            student.save()
            schema = request.scheme+"://"
            send_email_from_template(
                'email_welcome_academy', request.user.email,
                {
                    "url": request.build_absolute_uri(reverse('courses')),
                    "student": student,
                    'domain': schema+request.get_host(),
                },
                enqueued=False,
                user=None)
            messages.success(
                request, _('Thank you, We will send you an email soon'))
            return redirect(reverse('courses'))
        else:
            return redirect(reverse('courses'))
    return render(request, 'student_add.html')


def confirm_email(request):
    id = request.GET.get('id', -1)
    key = request.GET.get('key', '')

    try:
        student = Student.objects.get(pk=id)
    except Student.DoesNotExist:
        return render(
            request, 'messages.html', {
                'message': _('Key not found'), 'mtype': 'warning'})
    try:
        student.confirm(key)
        if student.user.is_active:
            return render(
                request, 'messages.html', {
                    'message': "Felicidades tu cuenta ha sido validada, ya puedes iniciar sesión.",
                    'mtype': 'success'})
    except Exception as e:
        print(e)
        pass

    return render(
        request, 'messages.html', {
            'message': _('Key not found'), 'mtype': 'warning'})


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
    token = request.GET.get('key','')
    student = get_object_or_404(Student, key=token)
    if request.method == 'GET':
        form = StudentResetPasswordForm(initial=student.__dict__)
    else:
        form = StudentResetPasswordForm(request.POST)
        if form.is_valid():
            student.user.set_password(form.cleaned_data['password'])
            student.user.save()
            student.key = uuid.uuid4()
            student.save()
            messages.success(request, "La contraseña ha sido cambiada con éxito.")
            return render(request, 'recover_password.html', {"student": student})
        else:
            messages.error(request, "No fue posible actualizar la contraseña.")
    return render(request, 'recover_password.html', {"form": form, "student": student})


@ajax
def mail_recover_pass(request):
    email = request.POST.get('email', 'no-email')
    students = Student.objects.filter(user__email__exact=email)
    if students:
        student = students[0]
        schema = request.scheme+"://"
        send_email_from_template(
                'email_recovery_academy', request.user.email, {
                    'url': request.build_absolute_uri(
                        reverse('recover_password')),
                    'domain': schema+request.get_host(),
                    'user': student.user,
                    'student': student,
                },
                enqueued=False,
                user=None)
        recover_message_type = 'success'
        recover_message = _('You will recive a message soon, check your email')
    else:
        recover_message_type = 'warning'
        recover_message = _('User not found')
    return {
        'inner-fragments': {
            '#recover_pass': render_to_string(
                'recover.html', context={
                    'recover_message_type': recover_message_type,
                    'recover_message': recover_message})}}


@login_required
def get_profile(request):
    return redirect(reverse('myprofile', kwargs={'pk': request.user.pk}))



#@method_decorator(login_required, name='dispatch')
class ProfessorProfileView(DetailView):
    model = Professor
    template_name = "professor/professor_profile.html"


@method_decorator(login_required, name='dispatch')
class StudentEdit(SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = "matricula/student_form.html"
    success_message = "Perfil actualizado con éxito"

    def get_context_data(self, **kwargs):
        context = UpdateView.get_context_data(self, **kwargs)
        enroll = Enroll.objects.filter(student__user=self.object).order_by('enroll_date')
        context['enroll'] = enroll.filter(enroll_activate=True, enroll_finished=True)
        context['pre_enroll'] = enroll.filter(enroll_finished=False)
        if hasattr(self.request.user, 'student'):
            context['student_form'] = StudentEditForm(initial=self.request.user.student.__dict__)
        if hasattr(self.request.user, 'professor'):
            context['professor_form'] = ProfessorEditProfileForm(initial=self.request.user.professor.__dict__)
        return context

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('myprofile', kwargs={'pk': pk})

    def post(self, request, *args, **kwargs):
        professor_form = None
        student_form = None
        errors = False
        self.object = self.get_object()
        if hasattr(request.user, 'professor'):
            professor_form = ProfessorEditProfileForm(request.POST)
            tmpupload = ChunkedUpload.objects.filter(upload_id=request.POST.get("photo")).first()
            if professor_form.is_valid():
                professor = request.user.professor
                professor.email = professor_form.cleaned_data['email_professor']
                professor.description = professor_form.cleaned_data['description']
                if tmpupload: 
                    professor.photo = tmpupload.get_uploaded_file()
                    tmpupload.delete()
                professor.save()
            else:
                errors = True
        if hasattr(request.user, 'student'):
            student_form = StudentEditForm(request.POST)
            if student_form.is_valid():
                student = request.user.student
                student.phone_number = student_form.cleaned_data['phone_number']
                student.country = student_form.cleaned_data['country']
                student.city = student_form.cleaned_data['city']
                student.organization = student_form.cleaned_data['organization']
                student.save()
            else:
                errors = False
        form = UserEditForm(request.POST, initial={"username":request.user.username})
        user = request.user
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()
        else:
            errors = True
        if errors:
            messages.error(request, _("We have some validations errors"))
            return self.render_to_response(self.get_context_data(
                form=form, student_form=student_form, professor_form=professor_form))
        else:
            messages.success(request, _("Profile updated successfully"))
        return super(StudentEdit, self).get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


def login_user(request):
    if not request.user.is_anonymous and not request.user.is_staff:
        messages.info(request, _('Your user have not permission for see this page'))
        return redirect(reverse('courses'))

    else:
        return render(request, 'student_login.html')


def parse_form_errors(form):
    msgs = ' - '
    fields = list(form.fields.keys())
    for field in fields:
        if form[field].errors:
            for message in form[field].errors:
                msgs += message
    return msgs
