import datetime
import json

from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django_ajax.decorators import ajax

from async_notifications.utils import send_email_from_template
from matricula.contrib.bills.models import Bill
from matricula.forms import CouponsSearchForm, CouponAddForm, CouponEditForm
from matricula.models import Coupon, Group, Student, Enroll
from django.utils.encoding import smart_text
from django.db import transaction
from django.core.exceptions import ValidationError

redirect_coupons = False


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


def get_error_message(request, student):
    request.session['redirect_coupons'] = False
    return messages.error(request, "Error, al estudiante " + str(student) + " no es posible asignarle"
            " este cupón, por favor verifique la cantidad de cupones asignados a este estudiante con el"
            " curso indicado, además verifique que los porcentajes de descuento asignados en un curso"
                                                            " no superen el 100%.")


def save_coupon(request, course, student, discount_percentage, coupon):

    coupon.group = course
    coupon.student = student
    coupon.discount_percentage = int(discount_percentage)
    coupon.save()
    if coupon.data_changed(['student_id', 'group_id', 'discount_percentage', 'is_used', 'code', 'bill_id']):
        schema = request.scheme+"://"
        send_email_from_template(
            "coupon_code_notification_updated",
            coupon.student.user.email,
            enqueued=False,
            user=student.user,
            context={'coupon': coupon, 'domain': schema+request.get_host(),}
        )
    messages.success(request, "El cupón ha sido actualizado éxitosamente.")
    request.session['redirect_coupons'] = True


def update_coupon(request, check_coupon, student, course, discount_percentage, coupon):
    year = datetime.datetime.now().year
    code = "UP" + str(year) + str(student)[0:2] + "P" + str(discount_percentage) + str(course)[0:2]
    code_counts = check_coupon.first().code[9]

    if code_counts == "5":
        code = "UP" + str(year) + str(student)[0:2] + "P2" + str(discount_percentage) + str(course)[0:2]

    if check_coupon.count() <= 1:
        if student == coupon.student:
            if not course == coupon.group:
                coupon.code = code
            save_coupon(request, course, student, discount_percentage, coupon)
        else:
            if check_coupon.first().discount_percentage == 50 and int(discount_percentage) == 50:
                coupon.code = code
                save_coupon(request, course, student, discount_percentage, coupon)
            else:
                get_error_message(request, student)
    else:
        cupon_exists = check_coupon.filter(pk=coupon.pk).first()

        if cupon_exists and check_coupon.count() == 2:

            if check_coupon.first().discount_percentage == 50 and check_coupon.last().discount_percentage == 50 and int(
                    discount_percentage) == 50:
                save_coupon(request, course, student, discount_percentage, coupon)
            else:
                get_error_message(request, student)
        else:
            get_error_message(request, student)


@permission_required('matricula.view_coupon')
def coupons_list(request):

    filters = {}
    coupons_list = Coupon.objects.all()
    request.session['redirect_coupons'] = False
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

            group = form.cleaned_data['group']
            student_list = form.cleaned_data['student']
            discount_percentage = form.cleaned_data['discount_percentage']

            student_error = ''

            if group and student_list and discount_percentage:
                try:
                    with transaction.atomic():

                        for student in student_list:

                            code = "UP" + str(year) + str(student)[0:2] + "P" + str(discount_percentage) + str(
                                            group)[0:2]

                            check_coupon = Coupon.objects.filter(student=student, group=group)

                            if check_coupon:

                                if check_coupon.count() == 1 and check_coupon.first().discount_percentage == 50 and discount_percentage == "50":

                                    if check_coupon.first().code[9] == "5":
                                        code = "UP" + str(year) + str(student)[0:2] + "P2" + str(discount_percentage) + str(group)[0:2]

                                    coupon = Coupon(
                                        student=student,
                                        group=group,
                                        code=code,
                                        discount_percentage=int(discount_percentage)
                                    )
                                    coupons_list.append(coupon)
                                else:
                                    student_error = str(student)
                                    send_coupons = False
                                    raise ValidationError("Something went grown with coupons assignment")

                            else:
                                coupon = Coupon(
                                        student=student,
                                        group=group,
                                        code=code,
                                        discount_percentage=int(discount_percentage)
                                    )
                                coupons_list.append(coupon)

                        if send_coupons:

                            if len(coupons_list) > 0:

                                coupons = Coupon.objects.bulk_create(coupons_list)
                                for coupon in coupons:
                                    bill = Bill.objects.filter(student=coupon.student,enrollment__group=coupon.group, is_paid=False).first()
                                    if bill:
                                        coupons_applied = Coupon.objects.filter(bill=bill)
                                        percentage = 0
                                        if coupons_applied:
                                            percentage = sum(coupons_applied.values_list('discount_percentage', flat=True))
                                        if percentage == 0:
                                            coupon.bill = bill
                                            if coupon.discount_percentage == 50:
                                                discount = bill.amount / 2
                                            else:
                                                discount = bill.amount
                                        elif percentage == 50 and coupon.discount_percentage==50:
                                            discount = bill.amount
                                            coupon.bill = bill
                                        else:
                                            discount = bill.amount
                                        bill.save()
                                        bill.description = render_to_string(
                                            'invoice_enroll.html',
                                            {
                                                'student': bill.student,
                                                'enroll': smart_text(bill.enrollment.group),
                                                'discount': discount,
                                                'total': bill.amount - discount,
                                                'date': bill.enrollment.enroll_date.strftime("%Y-%m-%d %H:%M"),
                                                'group': bill.enrollment.group,
                                            }
                                        )
                                        coupon.is_used = True
                                        coupon.save()
                                        bill.save()
                                send_code_notification(coupons_list, request.user, request)
                                messages.success(request, "El cupón ha sido registrado y se notificó al estudiante éxitosamente.")
                                return redirect('coupons_list')

                            else:
                                get_error_message(request, student)
                except ValidationError:
                    messages.error(request, f"Error el usuario {student_error} ya tiene el 100% de cupones en este curso")
                    return render(request, "coupons/create.html", context={'form': form})

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
    year = datetime.datetime.now().year
    redirect_coupons = request.session['redirect_coupons'] if 'redirect_coupons' in request.session else False

    if request.method == "POST":
        form = CouponEditForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            student = form.cleaned_data['student']
            discount_percentage = form.cleaned_data['discount_percentage']

            if group and student and discount_percentage:

                check_coupon = Coupon.objects.filter(student=student, group=group)

                if check_coupon:
                    update_coupon(request, check_coupon, student, group, discount_percentage, coupon)
                    if redirect_coupons:
                        return redirect('coupons_list')

                else:
                    coupon.code = "UP" + str(year) + str(student)[0:2] + "P" + str(discount_percentage) + str(group)[0:2]
                    save_coupon(request, group, student, discount_percentage, coupon)
                    return redirect('coupons_list')

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


def update_bill(bill, discount, total, percentage, code, enrollment, user, request):

    coupon = Coupon(
        course=enrollment.group.course,
        student=enrollment.student,
        discount_percentage=percentage,
        code=code
    )
    if bill:
        coupon.bill=bill
        coupon.is_used=True
    coupon.save()
    schema = request.scheme+"://"
    domain = schema+request.get_host()
    send_email_from_template(
        "coupon_code_notification",
        coupon.student.user.email,
        enqueued=False,
        user=user,
        context={'coupon': coupon, 'domain': domain}
    )

    if bill and enrollment:

        bill.description = render_to_string(
            'invoice_enroll.html',
            {
                'student': bill.student,
                'enroll': smart_text(bill.enrollment.group),
                'discount': discount,
                'total': total,
                'date': bill.enrollment.enroll_date.strftime("%Y-%m-%d %H:%M"),
                'group': bill.enrollment.group,
            }
        )
        bill.amount = total
        bill.save()


@ajax
def add_coupons_group(request, pk, percentage):

    group = get_object_or_404(Group, pk=pk)
    year = datetime.datetime.now().year

    if request.is_ajax():
       students = json.loads(request.body)

       for student_pk in students:
           student = get_object_or_404(Student, pk=int(student_pk['pk']))
           code = "UP" + str(year) + str(student)[0:2] + "P" + str(percentage) + str(group.course)[0:2]
           enrollment = Enroll.objects.filter(student=student, group=group).first()
           bill = Bill.objects.filter(enrollment=enrollment).first()
           discount = enrollment.group.cost
           total = 0.0

           if Coupon.objects.filter(student=student, group=group):

               if Coupon.objects.filter(student=student, group=group).count() == 1:

                   if Coupon.objects.filter(student=student, group=group).first().code[9] == "5" and percentage == 50:
                       code = "UP" + str(year) + str(student)[0:2] + "P2" + str(percentage) + str(group.course)[0:2]
                       update_bill(bill, discount, total, percentage, code, enrollment, request.user, request)
           else:
               if percentage == 50:
                   discount = enrollment.group.cost /2
                   total = enrollment.group.cost /2

               update_bill(bill, discount, total, percentage, code, enrollment, request.user, request)
