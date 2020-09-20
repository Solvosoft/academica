from async_notifications.models import NewsLetter, NewsLetterTemplate
from async_notifications.tasks import task_send_newsletter
from django.shortcuts import render, redirect

from membership_manager.newsletterform import NewsLetterTemplateForm, NewsLetterForm, FilterEmailsForm


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
                                                                        'lista_boletines': lista_boletines })


def create_news_letter(request, pk):
    template = NewsLetterTemplate.objects.get(pk=pk)


    if request.method == 'POST':
        form = NewsLetterForm(request.POST, pk=pk)
        form_filter = FilterEmailsForm(request.POST)

        if form.is_valid():
            news_letter = NewsLetter(
                template=template,
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message'],
                recipient=form.cleaned_data['recipient'],
                creator=request.user,
                file=form.cleaned_data['file'],
                create_datetime=form.cleaned_data['create_datetime'],
            )
            news_letter.save()

    else:
        form = NewsLetterForm(pk=pk)
        form_filter = FilterEmailsForm()

    return render(request, "news_letter/create_news_letter.html", context={'form': form, 'form_filter': form_filter})


def send_news_letter(request, pk):
    task_send_newsletter.delay(pk)
    return redirect('news_letter_list')

def delete_news_letter(request, pk):
    NewsLetter.objects.filter(pk=pk).delete()
    return redirect('news_letter_list')