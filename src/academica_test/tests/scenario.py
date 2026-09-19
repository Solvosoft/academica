"""
Fábricas de escenarios para las historias.

Las fechas de los grupos se calculan respecto a ``now()`` para dejarlos dentro de
la ventana que la historia necesita (prematrícula, matrícula o cerrada).
"""
from datetime import timedelta
from decimal import Decimal
from itertools import count

from django.conf import settings
from django.contrib.auth.models import Group as AuthGroup, User
from django.core.management import call_command
from django.utils import timezone

from matricula.models import Category, Course, Enroll, Group, Period, Professor, Student
from membership_core.models import Country, SystemCurrency

PASSWORD = 'Clave#Segura2026'
_seq = count(1)


def setup_roles():
    """Grupos Profesores / Administradores Académica con sus permisos."""
    call_command('permission_groups', verbosity=0)


def _user(prefix, **extra):
    n = next(_seq)
    username = extra.pop('username', '%s%d' % (prefix, n))
    user = User.objects.create_user(
        username, extra.pop('email', '%s@example.com' % username), PASSWORD,
        first_name=extra.pop('first_name', prefix.capitalize()),
        last_name=extra.pop('last_name', 'Prueba%d' % n), **extra)
    return user


def make_student(**extra):
    organization = extra.pop('organization', '[{"value": "UCR"}]')
    user = _user('estudiante', **extra)
    Student.objects.create(user=user, organization=organization, country=Country.objects.get(code='CR'),
                           city='San José', phone_number='88888888',
                           expired_at=timezone.now() + timedelta(days=15))
    return user


def make_professor(complete_profile=True, **extra):
    user = _user('profesor', **extra)
    group = AuthGroup.objects.get(name=settings.PROFESSOR_GROUP_NAME)
    user.groups.add(group)
    user.user_permissions.add(*group.permissions.all())
    Professor.objects.create(user=user, email=user.email if complete_profile else '',
                             description='Docente de pruebas' if complete_profile else '')
    return user


def make_academy_admin(**extra):
    user = _user('admin', **extra)
    user.groups.add(AuthGroup.objects.get(name=settings.ADMIN_GROUP_NAME))
    return user


def make_superuser(**extra):
    return _user('root', is_superuser=True, is_staff=True, **extra)


def currency(code='CRC'):
    return SystemCurrency.objects.get(currency=code)


def make_period(name=None):
    today = timezone.localdate()
    return Period.objects.create(name=name or 'Periodo %d' % next(_seq),
                                 start_date=today - timedelta(days=30),
                                 finish_date=today + timedelta(days=60))


def make_course(name=None, category=None):
    category = category or Category.objects.get_or_create(
        name='Programación', defaults={'description': 'Cursos de programación'})[0]
    return Course.objects.create(category=category, name=name or 'Curso %d' % next(_seq),
                                 content='<p>Contenido del curso</p>')


def window_dates(window):
    """Fechas de prematrícula y matrícula para que el grupo esté en ``window``."""
    now = timezone.now()
    day = timedelta(days=1)
    if window == 'pre':
        return dict(pre_enroll_start=now - day, pre_enroll_finish=now + day,
                    enroll_start=now + 2 * day, enroll_finish=now + 10 * day)
    if window == 'enroll':
        return dict(pre_enroll_start=now - 10 * day, pre_enroll_finish=now - 5 * day,
                    enroll_start=now - day, enroll_finish=now + 5 * day)
    if window == 'closed':
        return dict(pre_enroll_start=now - 20 * day, pre_enroll_finish=now - 15 * day,
                    enroll_start=now - 10 * day, enroll_finish=now - day)
    raise ValueError(window)


def move_group_to(group, window):
    for key, value in window_dates(window).items():
        setattr(group, key, value)
    group.save()
    return group


def make_group(course=None, period=None, window='enroll', flow=Group.AUTO_ENROLL, cost=0,
               currency_code='CRC', maximum=20, professors=(), name=None):
    group = Group.objects.create(
        course=course or make_course(), period=period or make_period(),
        name=name or 'Grupo %d' % next(_seq), schedule='Lunes 6pm',
        is_paid=cost > 0, cost=Decimal(cost), currency=currency(currency_code),
        maximum=maximum, is_open=True, flow=flow, **window_dates(window))
    for professor_user in professors:
        group.professors.add(professor_user.professor)
    return group


def enroll(student_user, group, **flags):
    defaults = dict(enroll_activate=True, enroll_finished=True)
    defaults.update(flags)
    return Enroll.objects.create(student=student_user.student, group=group, **defaults)
