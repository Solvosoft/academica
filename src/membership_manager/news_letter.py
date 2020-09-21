from async_notifications.models import NewsLetter, NewsLetterTemplate, NewsLetterTask
from async_notifications.tasks import task_send_newsletter
from django.shortcuts import render, redirect
from django.urls import reverse

from membership_manager.newsletterform import NewsLetterTemplateForm, NewsLetterForm, FilterEmailsForm, SentDate


def news_letter_list(request):

    if request.method == 'POST':
        form = NewsLetterTemplateForm(request.POST)

        if form.is_valid():
            news_letter_template = form.cleaned_data['news_letter_template'].pk
            return redirect('create_news_letter', pk=news_letter_template)

    else:
        form = NewsLetterTemplateForm()

    lista_boletines = NewsLetter.objects.all()

    return render(request, "news_letter/news_letter_list.html", context={'form': form,
                                                                        'lista_boletines': lista_boletines})
def create_news_letter(request, pk):
    template = NewsLetterTemplate.objects.get(pk=pk)
    form_sent_date = SentDate()
    news_letter = NewsLetter.objects.filter(subject="GuardadoPrueba").first()

    if news_letter is None:

        news_letter = NewsLetter(
            template=template,
            subject="GuardadoPrueba",
            message="",
            recipient="active=&apply_fees=&invoices=&busqueda_en=&excludeemail=",
            creator=request.user
        )
        news_letter.save()

    url_news_letter_task = reverse('api_news_letter_task', args=(news_letter.pk,))
    news_letter_task_list = [{'pk': obj.pk, 'name': obj.send_date} for obj in news_letter.newslettertask_set.all()]

    if request.method == 'POST':
        form = NewsLetterForm(request.POST, pk=pk)
        form_filter = FilterEmailsForm(request.POST)

        if form.is_valid():
            NewsLetter.objects.filter(pk=news_letter.pk).update(
                template=template,
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                recipient=form.cleaned_data['recipient'],
                creator=request.user,
                file=form.cleaned_data['file']
            )

    else:
        form = NewsLetterForm(pk=pk)
        form_filter = FilterEmailsForm()

    return render(request, "news_letter/create_news_letter.html", context={'form': form, 'form_filter': form_filter,
                                                                           'form_sent_date': form_sent_date,
                                                                           'news_letter_task_list': news_letter_task_list,
                                                                           'url_news_letter_task': url_news_letter_task})


def send_news_letter(request, pk):
    task_send_newsletter.delay(pk)
    return redirect('news_letter_list')

def delete_news_letter(request, pk):
    boletin = NewsLetter.objects.filter(pk=pk).first()

    if boletin:
        boletin.delete()
        return redirect('news_letter_list')