from django.shortcuts import render, redirect

from membership_manager.newsletterform import NewsLetterTemplateForm, NewsLetterForm


def news_letter(request):

    if request.method == 'POST':
        form = NewsLetterTemplateForm(request.POST)

        if form.is_valid():
            news_letter_template = form.cleaned_data['news_letter_template'].pk
            return redirect('create_news_letter', pk=news_letter_template)

    else:
        form = NewsLetterTemplateForm()

    return render(request, "news_letter/news_letter.html", context={'form': form})


def create_news_letter(request, pk):

    if request.method == 'POST':
        form = NewsLetterForm(request.POST, pk=pk)

    else:
        form = NewsLetterForm(pk=pk)

    return render(request, "news_letter/create_news_letter.html", context={'form': form})