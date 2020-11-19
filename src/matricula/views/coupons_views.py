import datetime

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect

from async_notifications.utils import send_email_from_template
from matricula.forms import CouponsSearchForm, CouponAddForm
from matricula.models import Coupon


def send_code_notification(coupons_list, user):

    for coupon in coupons_list:
        send_email_from_template(
            "coupon_code_notification",
            coupon.student.user.email,
            enqueued=False,
            user=user,
            context={'coupon': coupon}
        )


@permission_required('matricula.view_coupon')
def coupons_list(request):

    filters = {}
    coupons_list = Coupon.objects.all()

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

            coupons_list = Coupon.objects.filter(**filters)

    else:
        form = CouponsSearchForm()

    return render(request, "coupons/coupons_list.html", context={'form': form, 'coupons_list': coupons_list})


@permission_required('matricula.add_coupon')
def create_cupon(request):

    year = datetime.datetime.now().year

    if request.method == "POST":

        form = CouponAddForm(request.POST)

        if form.is_valid():

            course = form.cleaned_data['course']
            student_list = form.cleaned_data['student']
            discount_percentage = form.cleaned_data['discount_percentage']

            if course and student_list and discount_percentage:
                coupons_list = [Coupon(
                    student=student,
                    course=course,
                    code="UP" + str(year) + str(student)[0:2] + "P" + str(discount_percentage) + str(course)[0:2],
                    discount_percentage=discount_percentage
                ) for student in student_list]

                if coupons_list:

                    Coupon.objects.bulk_create(coupons_list)
                    send_code_notification(coupons_list, request.user)
                    messages.success(request, "El cupón ha sido registrado y se notifico al estudiante éxitosamente.")
                    return redirect('coupons_list')

    else:
        form = CouponAddForm()

    return render(request, "coupons/create.html", context={'form': form})