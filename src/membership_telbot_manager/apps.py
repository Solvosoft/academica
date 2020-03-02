from time import sleep

from django.apps import AppConfig
from django.conf import settings
import telebot


class MembershipTelbotManagerConfig(AppConfig):
    name = 'membership_telbot_manager'
    def ready(self):
        super().ready()
        if not settings.DEBUG or settings.TEST_TELEGRAM:
            self.initial_bot()

    def initial_bot(self):
        ok = False
        while not ok:
            try:
                bot = telebot.TeleBot(settings.TELEGRAM_BOT_API)
                bot.set_webhook(url=settings.TELEGRAM_BOT_WEBHOOK)
                ok=True
            except:
                sleep(3)