from django.http import QueryDict

from async_notifications.models import NewsLetter, NewsLetterTemplate, NewsLetterTask
from async_notifications.tasks import task_send_newsletter
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from membership_manager.models import Membership
from membership_manager.newsletterform import NewsLetterTemplateForm, NewsLetterForm, FilterEmailsForm, SendDateForm, \
    EmailsNewsLetter, TemplateBaseNewsLetterForm


def news_letter_list(request):

    if request.method == 'POST':
        form = NewsLetterTemplateForm(request.POST)

        if form.is_valid():
            news_letter_template = form.cleaned_data['news_letter_template'].pk
            return redirect('create_news_letter', pk=news_letter_template)

    else:
        form = NewsLetterTemplateForm()

    lista_boletines = NewsLetter.objects.all()
    send_date_form = SendDateForm()

    return render(request, "news_letter/news_letter_list.html", context={'form': form,
                                                                         'send_date_form': send_date_form,
                                                                         'lista_boletines': lista_boletines})
def create_news_letter(request, pk):
    template = get_object_or_404(NewsLetterTemplate, pk=pk)
    emails_organization = Membership.objects.all().exclude(organization__email__isnull=True).values_list('organization__email', flat=True)
    emails_contacts = Membership.objects.all().exclude(contact__email__isnull=True).values_list('contact__email', flat=True)
    emails = list(emails_organization) + list(emails_contacts)

    if request.method == 'POST':
        form = NewsLetterForm(request.POST)
        form_filter = FilterEmailsForm(request.POST)

        if form.is_valid():
            news_letter = NewsLetter(
                template=template,
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                recipient=form.cleaned_data['recipient'],
                creator=request.user,
                file=form.cleaned_data['file'],
                filters=form.cleaned_data['filters']
            )
            news_letter.save()
            return redirect('news_letter_list')
    else:
        form = NewsLetterForm(initial={'message': template.message})
        form_filter = FilterEmailsForm()


    return render(request, "news_letter/create_news_letter.html", context={'form': form,
                                                                           'template': pk,
                                                                           'form_filter': form_filter})


def send_news_letter(request, pk):
    task_send_newsletter.delay(pk)
    return redirect('news_letter_list')

def delete_news_letter(request, pk):
    boletin = NewsLetter.objects.filter(pk=pk).first()

    if boletin:
        boletin.delete()
        return redirect('news_letter_list')


class EditNewsLetter(UpdateView):
    model = NewsLetter
    form_class = NewsLetterForm
    template_name = 'news_letter/edit_news_letter.html'
    success_url = reverse_lazy('news_letter_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news_letter = context['object']
        form_filter = FilterEmailsForm(QueryDict(news_letter.filters))
        context.update({'form_filter': form_filter ,
                        'template': news_letter.template.pk,
                        })
        return context


def create_task(request, pk):
    boletin = NewsLetter.objects.filter(pk=pk).first()

    if request.method == 'POST':

        form = SendDateForm(request.POST)

        if form.is_valid():

            task = NewsLetterTask(
                template=boletin,
                send_date=form.cleaned_data['send_date']
            )
            task.save()
            messages.success(request, 'Fecha de envío registrada exitosamente.')
            return redirect('news_letter_list')
        else:
            messages.error(request, 'La fecha y hora ingresada no debe ser inferior a la fecha y hora actual.')
            return redirect('news_letter_list')



def delete_task(request, pk):
    task = NewsLetterTask.objects.filter(pk=pk).first()

    if task:
        task.delete()
        return redirect('news_letter_list')


def create_news_letter_template(request):

    if request.method == "POST":

        form = TemplateBaseNewsLetterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('news_letter_list')
    else:
        form = TemplateBaseNewsLetterForm()

    return render(request, "news_letter/create_news_letter_template.html", context={'form': form})