from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from membership_manager.models import Organization

class TelGroup(models.Model):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE,null=True,blank=True,related_name='telgroup')
    chat_id = models.IntegerField()
    title = models.CharField(max_length=250)
    invite_link = models.URLField(null=True,blank=True)

    class Meta:
        verbose_name = "Grupo de Telegram"
        verbose_name_plural = "Grupos de Telegram"

    def __str__(self):
        return "%s" % (
            self.title
        )

class TelegramUser(models.Model):
    user = models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE)
    group = models.ForeignKey(TelGroup,models.CASCADE)
    telegram_id = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Usuarios de Telegram"
        verbose_name_plural = "Usuarios de Telegram"

    def __str__(self):
        return "%s - %s %s" % (
            self.username,self.first_name,self.last_name
        )