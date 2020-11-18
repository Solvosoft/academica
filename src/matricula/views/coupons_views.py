from django.contrib.auth.decorators import permission_required
from django.shortcuts import render

from matricula.forms import CouponsSearchForm
from matricula.models import Coupon


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