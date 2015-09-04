from django.shortcuts import render

# Create your views here.

from django.utils.cache import get_language
from django import forms
from simplemathcaptcha.fields import MathCaptchaField
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

class featureForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, label=_('Your text'))
    captcha = MathCaptchaField()


def render_temp(request, slug):
    lang = "es"
    if get_language() == 'en':
        lang = "en"
    template = slug + "_" + lang + ".html"
    return render(request, template)


def feature(request, slug):
    lang = "es"
    if get_language() == 'en':
        lang = "en"
    template = slug + "_" + lang + ".html"

    values = {}
    form_fail = False
    if request.method == 'POST':
        form_fail = True
        form = featureForm(request.POST)
        if form.is_valid():
            subject = 'Feature in Academica'
            message = form.cleaned_data['text']
            sender = 'info@solvosoft.com'
            recipients = ['info@solvosoft.com']
            send_mail(subject, message, sender, recipients)
            values['success'] = True
            form_fail = False
    if not form_fail:
        form = featureForm()

    values['form'] = form
    return render(request, template, context=values)
