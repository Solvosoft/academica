from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.http import QueryDict
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from async_notifications.models import NewsLetter, NewsLetterTemplate, NewsLetterTask
from async_notifications.tasks import task_send_newsletter
from membership_manager.newsletterform import NewsLetterTemplateForm, NewsLetterForm, FilterEmailsForm, SendDateForm, \
    TemplateBaseNewsLetterForm


@permission_required('async_notifications.view_newsletter')
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


@permission_required('async_notifications.add_newsletter')
def create_news_letter(request, pk):
    template = get_object_or_404(NewsLetterTemplate, pk=pk)

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
            messages.success(request, "Boletín registrado con éxito")
            return redirect('news_letter_list')
    else:
        form = NewsLetterForm(initial={'message': template.message})
        form_filter = FilterEmailsForm()

    return render(request, "news_letter/create_news_letter.html", context={'form': form,
                                                                           'template': pk,
                                                                           'form_filter': form_filter})


def send_news_letter(request, pk):
    task_send_newsletter.delay(pk)
    messages.success(request, "Envío de boletín éxitoso")
    return redirect('news_letter_list')


@permission_required('async_notifications.delete_newsletter')
def delete_news_letter(request, pk):
    boletin = NewsLetter.objects.filter(pk=pk).first()

    if boletin:
        boletin.delete()
        messages.success(request, "Boletín eliminado con éxito")
        return redirect('news_letter_list')


@method_decorator(permission_required('async_notifications.change_newsletter'), name='dispatch')
class EditNewsLetter(UpdateView):
    model = NewsLetter
    form_class = NewsLetterForm
    template_name = 'news_letter/edit_news_letter.html'
    success_url = reverse_lazy('news_letter_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        news_letter = context['object']
        form_filter = FilterEmailsForm(QueryDict(news_letter.filters))
        context.update({'form_filter': form_filter,
                        'template': news_letter.template.pk,
                        })
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Boletín actualizado con éxito")
        return super().form_valid(form)


@permission_required('async_notifications.add_newslettertask')
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
            messages.success(request, 'Fecha de envío registrada con éxito')
            return redirect('news_letter_list')
        else:
            messages.error(request, 'La fecha y hora ingresada no debe ser inferior a la fecha y hora actual.')
            return redirect('news_letter_list')


@permission_required('async_notifications.delete_newslettertask')
def delete_task(request, pk):
    task = NewsLetterTask.objects.filter(pk=pk).first()

    if task:
        task.delete()
        messages.success(request, "Fecha de envío eliminada con éxito")
        return redirect('news_letter_list')


@permission_required('async_notifications.add_newslettertemplate')
def create_news_letter_template(request):
    if request.method == "POST":

        form = TemplateBaseNewsLetterForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Plantilla base de boletín registrada con éxito")
            return redirect('news_letter_list')
    else:
        form = TemplateBaseNewsLetterForm()

    return render(request, "news_letter/create_news_letter_template.html", context={'form': form})


@permission_required('async_notifications.add_newsletter')
def create_news_letter_membership(request):

    templateform = NewsLetterTemplateForm(request.GET)
    templateform.is_valid()
    template = get_object_or_404(NewsLetterTemplate, pk=templateform.cleaned_data['news_letter_template'].pk)
    querydictfilters = QueryDict('', mutable=True)
    auxquerydict = QueryDict('', mutable=True)
    querydictfilters.update(request.GET)
    auxquerydict.update({'apply_filters': 'True'})
    querydictfilters.update(auxquerydict)
    form_filter = FilterEmailsForm(querydictfilters)
    form_filter.is_valid()
    form = NewsLetterForm(initial={'message': template.message})

    return render(request, "news_letter/create_news_letter.html", context={'form': form,
                                                                           'template': template.pk,
                                                                           'form_filter': form_filter})