
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from matricula.contrib.bills.models import Sale, Bill
from matricula.contrib.bills.forms import SalePaymentForm


def stripe_charge(request, pk):
    bill = get_object_or_404(Bill, pk=pk, student=request.user)
    new_form = True
    message = ""
    if request.method == "POST":
        form = SalePaymentForm(request.POST, initial={'billid': bill.pk})

        if form.is_valid():  # charges the card
            message = _("Success! We have charged your card!")
            new_form = True
        else:
            message = _("ERROR! We have not charged your card!")
            new_form = False

    if new_form:
        form = SalePaymentForm(initial={'bill':bill.pk})

    return render_to_response("stripe_charge.html",
                        RequestContext(request, {'message': message,
                                                 'form': form,
                                                 'bill': bill}))
