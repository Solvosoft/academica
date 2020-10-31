from django import forms
from djgentelella.widgets import core as genwidgets
from djgentelella.forms.forms import GTForm

from membership_telbot_manager.models import TelegramNotificationTemplate


class TelegramNotificationTemplateForm(GTForm, forms.Form):

    template = forms.ModelChoiceField(widget=genwidgets.Select,
                                  queryset=TelegramNotificationTemplate.objects.all(), label="Plantilla", required=True)