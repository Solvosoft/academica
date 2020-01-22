from django.apps import AppConfig
from django.conf import settings
import telebot

class MembershipTelbotManagerConfig(AppConfig):
    name = 'membership_telbot_manager'
    def ready(self):
        super().ready()

        bot = telebot.TeleBot(settings.TELEGRAM_BOT_API)
        bot.set_webhook(url=settings.TELEGRAM_BOT_WEBHOOK)