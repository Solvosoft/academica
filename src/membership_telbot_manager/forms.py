from django import forms
from djgentelella.widgets import core as genwidgets, wysiwyg
from djgentelella.forms.forms import GTForm

from membership_telbot_manager.models import TelegramNotificationTemplate, TelGroup


class TelegramNotificationTemplateForm(GTForm, forms.Form):

    template = forms.ModelChoiceField(widget=genwidgets.Select,
                                  queryset=TelegramNotificationTemplate.objects.all(), label="Plantilla", required=True)


class TelGroupForm(GTForm, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['title'].label = "Título"
        self.fields['chat_id'].required = False
        self.fields['chat_id'].label = "Id del grupo"
        self.fields['invite_link'].label = "Enlace de invitación"

    field_order = ['title', 'chat_id', 'invite_link']

    class Meta:
        model = TelGroup
        exclude = ['organization']

        widgets = {
            'title': genwidgets.TextInput,
            'chat_id': genwidgets.TextInput,
            'invite_link': genwidgets.URLInput,
        }


class TelegramNotificationTemplateEdit(GTForm, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].disabled = True

    class Meta:
        model = TelegramNotificationTemplate
        fields = '__all__'

        widgets = {
            'name': genwidgets.TextInput,
            'description': genwidgets.Textarea,
        }
