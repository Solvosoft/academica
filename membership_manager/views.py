from django.contrib import messages
from django.shortcuts import render, redirect


# Create your views here.


def create_membership_contact_by_template(request):

    messages.error(request, "Sorry data is not valid")
    return redirect(request.META['HTTP_REFERER'])