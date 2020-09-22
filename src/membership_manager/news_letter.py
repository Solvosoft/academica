from async_notifications.models import NewsLetter, NewsLetterTemplate, NewsLetterTask
from async_notifications.tasks import task_send_newsletter
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import UpdateView

from membership_manager.models import Membership
from membership_manager.newsletterform import NewsLetterTemplateForm, NewsLetterForm, FilterEmailsForm, SendDateForm, \
    EmailsNewsLetter


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

    if request.method == 'POST':
        form = NewsLetterForm(request.POST, pk=pk, initial={'template': pk, 'creator': request.user.pk})
        form_filter = FilterEmailsForm(request.POST)

        if form.is_valid():
            news_letter = NewsLetter(
                template=template,
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                recipient=form.cleaned_data['recipient'],
                creator=request.user,
                file=form.cleaned_data['file']
            )
            news_letter.save()
    else:
        form = NewsLetterForm(pk=pk, initial={'template': pk, 'creator': request.user.pk})
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
        news_letter_task_list = [{'pk': obj.pk, 'name': obj.send_date} for obj in news_letter.newslettertask_set.all()]
        url_news_letter_task = reverse('api_news_letter_task', args=(news_letter.pk,))
        form_sent_date = SendDateForm()
        form_filter = FilterEmailsForm()
        context.update({'form_filter': form_filter,
                        'form_sent_date': form_sent_date,
                        'news_letter_task_list': news_letter_task_list,
                        'url_news_letter_task': url_news_letter_task
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