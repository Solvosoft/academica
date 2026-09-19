import json

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from matricula.ajax import ajax

from djgentelella.async_notification.sending import send_email_from_template
from matricula.contrib.bills.models import Bill
from matricula.forms import CouponsSearchForm, CouponAddForm, CouponEditForm
from matricula import coupons
from matricula.models import Coupon, Group, Student
from django.db import transaction


def send_code_notification(coupons_list, user, request):

    schema = request.scheme+"://"
    domain = schema+request.get_host()
    for coupon in coupons_list:
        send_email_from_template(
            "coupon_code_notification",
            coupon.student.user.email,
            enqueued=True,
            user=user,
            context={'coupon': coupon, 'domain': domain}
        )


@permission_required('matricula.view_coupon')
def coupons_list(request):

    filters = {}
    coupons_list = Coupon.objects.all()
    has_data = coupons_list.exists()
    if request.method == "GET":

        form = CouponsSearchForm(request.GET)
        if form.is_valid():

            group = form.cleaned_data['group']
            student = form.cleaned_data['student']
            is_used = form.cleaned_data['is_used']
            discount_percentage = form.cleaned_data['discount_percentage']

            if group:
                filters['group__in'] = group

            if student:
                filters['student__in'] = student

            if is_used:
                filters['is_used'] = is_used

            if discount_percentage:
                filters['discount_percentage'] = discount_percentage

            coupons_list = Coupon.objects.filter(**filters)

    else:
        form = CouponsSearchForm()

    return render(request, "coupons/coupons_list.html", 
            context={'form': form, 'coupons_list': coupons_list, 'has_data':has_data})


@permission_required('matricula.add_coupon')
def create_cupon(request):
    if request.method == "POST":
        form = CouponAddForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            student_list = form.cleaned_data['student']
            percentage = int(form.cleaned_data['discount_percentage'])
            rejected = [student for student in student_list if not coupons.can_add(student, group, percentage)]
            if rejected:
                messages.error(request, "Error el usuarie %s ya tiene el 100%% de cupones en este curso"
                               % ", ".join(str(student) for student in rejected))
                return render(request, "coupons/create.html", context={'form': form})
            with transaction.atomic():
                created = [coupons.create_coupon(student, group, percentage) for student in student_list]
            send_code_notification(created, request.user, request)
            messages.success(request, "El cupón ha sido registrado y se notificó al estudiante éxitosamente.")
            return redirect('coupons_list')
    else:
        form = CouponAddForm()
    return render(request, "coupons/create.html", context={'form': form})


@permission_required('matricula.delete_coupon')
@require_POST
def delete_coupon(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    error = coupons.delete_coupon(coupon)
    if error:
        messages.error(request, error)
    else:
        messages.success(request, "Cupón eliminado con éxito")
    return redirect('coupons_list')


@permission_required('matricula.change_coupon')
def edit_coupon(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    if request.method == "POST":
        form = CouponEditForm(request.POST)
        if form.is_valid() and all(form.cleaned_data.get(k) for k in ('student', 'group', 'discount_percentage')):
            data = form.cleaned_data
            changed = (data['student'], data['group'], int(data['discount_percentage'])) != (
                coupon.student, coupon.group, coupon.discount_percentage)
            error = coupons.update_coupon(coupon, data['student'], data['group'], data['discount_percentage'])
            if error:
                messages.error(request, error)
            else:
                if changed:
                    send_email_from_template(
                        "coupon_code_notification_updated", coupon.student.user.email,
                        enqueued=False, user=request.user,
                        context={'coupon': coupon, 'domain': request.scheme + "://" + request.get_host()})
                messages.success(request, "El cupón ha sido actualizado éxitosamente.")
                return redirect('coupons_list')
        elif form.is_valid():
            messages.error(request, "Estudiante, grupo y descuento son obligatorios.")
    else:
        form = CouponEditForm(initial={
            'student': coupon.student,
            'group': coupon.group,
            'discount_percentage': coupon.discount_percentage
        })
    return render(request, "coupons/create.html", context={'form': form})


@permission_required('matricula.view_coupon')
def coupons_bill_list(request, pk):

    bill = get_object_or_404(Bill, pk=pk)

    filters = {}
    coupons_list = Coupon.objects.filter(bill=bill)

    if request.method == "GET":

        form = CouponsSearchForm(request.GET)
        if form.is_valid():

            course = form.cleaned_data['course']
            student = form.cleaned_data['student']
            is_used = form.cleaned_data['is_used']
            discount_percentage = form.cleaned_data['discount_percentage']

            if course:
                filters['course__in'] = course

            if student:
                filters['student__in'] = student

            if is_used:
                filters['is_used'] = is_used

            if discount_percentage:
                filters['discount_percentage'] = discount_percentage

            coupons_list = coupons_list.filter(**filters)

    else:
        form = CouponsSearchForm()

    return render(request, "coupons/coupons_list.html", context={'form': form, 'coupons_list': coupons_list})


@ajax
@permission_required('matricula.add_coupon')
def add_coupons_group(request, pk, percentage):
    """Asigna cupones a los estudiantes marcados en la lista de pre-inscritos."""
    group = get_object_or_404(Group, pk=pk)
    if percentage not in (50, 100):
        return {'error': "Porcentaje inválido"}
    student_pks = [int(item['pk']) for item in json.loads(request.body or b'[]') if item.get('pk')]
    students = list(Student.objects.filter(pk__in=student_pks, enroll__group=group).distinct())
    rejected = [str(student) for student in students if not coupons.can_add(student, group, percentage)]
    if not students or rejected:
        return {'error': "No se asignaron cupones. %s" % (
            ("Ya tienen el 100%% de descuento: %s" % ", ".join(rejected)) if rejected
            else "No se seleccionaron estudiantes.")}
    with transaction.atomic():
        created = [coupons.create_coupon(student, group, percentage) for student in students]
    send_code_notification(created, request.user, request)
    return {'assigned': len(created)}
