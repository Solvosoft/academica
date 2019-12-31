from django.contrib import admin

# Register your models here.
from membership_telbot_manager import models

admin.site.register(models.TelegramUser)
admin.site.register(models.TelGroup)