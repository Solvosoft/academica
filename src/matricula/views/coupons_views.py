import datetime

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect

from async_notifications.utils import send_email_from_template
from matricula.forms import CouponsSearchForm, CouponAddForm, CouponEditForm
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

    coupons_list = []
    send_coupons = True
    student = ""

    year = datetime.datetime.now().year

    if request.method == "POST":

        form = CouponAddForm(request.POST)

        if form.is_valid():

            course = form.cleaned_data['course']
            student_list = form.cleaned_data['student']
            discount_percentage = form.cleaned_data['discount_percentage']

            if course and student_list and discount_percentage:
                for student in student_list:

                    check_coupon = Coupon.objects.filter(student=student, course=course)

                    if check_coupon:

                        if check_coupon.count() == 1 and check_coupon.first().discount_percentage == 50 and discount_percentage == "50":
                            coupon = Coupon(
                                student=student,
                                course=course,
                                code="UP" + str(year) + str(student)[0:2] + "P2" + str(discount_percentage) + str(
                                    course)[0:2],
                                discount_percentage=int(discount_percentage)
                            )
                            coupons_list.append(coupon)
                        else:
                            student = str(student)
                            send_coupons = False
                            break


                    else:
                        coupon = Coupon(
                                student=student,
                                course=course,
                                code="UP" + str(year) + str(student)[0:2] + "P" + str(discount_percentage) + str(
                                    course)[0:2],
                                discount_percentage=int(discount_percentage)
                            )
                        coupons_list.append(coupon)

                if send_coupons:

                    if coupons_list:

                        Coupon.objects.bulk_create(coupons_list)
                        send_code_notification(coupons_list, request.user)
                        messages.success(request, "El cupón ha sido registrado y se notificó al estudiante éxitosamente.")
                        return redirect('coupons_list')
                else:
                    messages.error(request, "Error, al estudiante " + student + " no es posible asignarle"
                                                                                     " este cupón, por favor verifique la cantidad de cupones asignados a este estudiante con el"
                                                                                     " curso indicado, además verifique que los porcentajes de descuento asignados en un curso"
                                                                                     " no superen el 100%.")

    else:
        form = CouponAddForm()

    return render(request, "coupons/create.html", context={'form': form})


@permission_required('matricula.delete_coupon')
def delete_coupon(request, pk):
    coupon = Coupon.objects.filter(pk=pk).first()

    if coupon:
        coupon.delete()
        messages.success(request, "Cupón eliminado con éxito")
        return redirect('coupons_list')


@permission_required('matricula.change_coupon')
def edit_coupon(request, pk):
    coupon = Coupon.objects.filter(pk=pk).first()

    if request.method == "POST":
        form = CouponEditForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            student = form.cleaned_data['student']
            discount_percentage = form.cleaned_data['discount_percentage']

            if course and student and discount_percentage:

                check_coupon = Coupon.objects.filter(student=student, course=course)

                if check_coupon:

                    if check_coupon.count() <= 1:
                        if student == coupon.student:
                            coupon.course = course
                            coupon.student = student
                            coupon.discount_percentage = int(discount_percentage)
                            coupon.save()
                            messages.success(request, "El cupón ha sido actulizado y se notificó al estudiante éxitosamente.")
                            return redirect('coupons_list')

                        else:
                            if check_coupon.first().discount_percentage == 50 and int(discount_percentage) == 50:
                                coupon.course = course
                                coupon.student = student
                                coupon.discount_percentage = int(discount_percentage)
                                coupon.save()
                                messages.success(request,
                                                 "El cupón ha sido actualizado y se notificó al estudiante éxitosamente.")
                                return redirect('coupons_list')
                            else:
                                messages.error(request,
                                               "Error, al estudiante " + str(student) + " no es posible asignarle"
                                                                                        " este cupón, por favor verifique la cantidad de cupones asignados a este estudiante con el"
                                                                                        " curso indicado, además verifique que los porcentajes de descuento asignados en un curso"
                                                                                        " no superen el 100%.")
                    else:

                        cupon_exists = check_coupon.filter(pk=coupon.pk).first()

                        if cupon_exists and check_coupon.count() == 2:

                            if check_coupon.first().discount_percentage == 50 and check_coupon.last().discount_percentage == 50 and int(discount_percentage) == 50:
                                coupon.course = course
                                coupon.student = student
                                coupon.discount_percentage = int(discount_percentage)
                                coupon.save()
                                messages.success(request, "El cupón ha sido actualizado y se notificó al estudiante éxitosamente.")
                                return redirect('coupons_list')
                            else:
                                messages.error(request,
                                               "Error, al estudiante " + str(student) + " no es posible asignarle"
                                                                                   " este cupón, por favor verifique la cantidad de cupones asignados a este estudiante con el"
                                                                                   " curso indicado, además verifique que los porcentajes de descuento asignados en un curso"
                                                                                   " no superen el 100%.")
                        else:
                            messages.error(request,
                                           "Error, al estudiante " + str(student) + " no es posible asignarle"
                                                                               " este cupón, por favor verifique la cantidad de cupones asignados a este estudiante con el"
                                                                               " curso indicado, además verifique que los porcentajes de descuento asignados en un curso"
                                                                               " no superen el 100%.")

    else:
       form = CouponEditForm(initial={
            'student': coupon.student,
            'course': coupon.course,
            'discount_percentage': coupon.discount_percentage
        })

    return render(request, "coupons/create.html", context={'form': form})