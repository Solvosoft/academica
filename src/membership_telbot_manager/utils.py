from membership_manager.models import Invoice, Membership
from membership_telbot_manager.models import TelGroup, TelegramNotificationTemplate
from django.template import Context, Template
import telebot
from django.conf import settings
bot = telebot.TeleBot(settings.TELEGRAM_BOT_API)


def get_telegram_group(membership):
    if membership.organization:
        return TelGroup.objects.filter(organization_id=membership.organization.pk).first()


def expiration_message(organization, chat_id):

    template = TelegramNotificationTemplate.objects.filter(name="Mensaje de expiración").first()
    message = Template(template.description)
    msgg = message.render(Context({'organization':organization}))
    bot.send_message(chat_id, msgg)


def help_dialog(chat_id):

    template = TelegramNotificationTemplate.objects.filter(name="Diálogo de ayuda").first()
    message = Template(template.description)
    msgg = message.render(Context({'chat_id': str(chat_id)}))
    bot.send_message(chat_id, text=msgg)


def invoices(chat_id):
    telgroup = TelGroup.objects.filter(chat_id=chat_id).first()
    if telgroup:
        invoices = Invoice.objects.filter(
            membership__state='active',
            membership__organization=telgroup.organization,
            status='pending')

        template = TelegramNotificationTemplate.objects.filter(name="Facturas").first()

        message = Template(template.description)
        msgg = message.render(Context({'invoices': invoices,
                                       'memberships': Membership.objects.filter(state="active",
                                                                                organization=telgroup.organization)
                                       }))
        bot.send_message(chat_id, text=msgg)


def memberships(chat_id):
    telgroup = TelGroup.objects.filter(chat_id=chat_id).first()
    if telgroup:
        memberships = telgroup.organization.membership_set.all()
        if memberships:
            context = {'memberships': memberships, 'option': "membresias", 'title': telgroup.organization.name}
        else:
            new_text = "No cuenta con membresias.\n"
            context = {'memberships': new_text, 'option': "none", 'title': telgroup.organization.name}

        template = TelegramNotificationTemplate.objects.filter(name="Membresías").first()
        message = Template(template.description)
        msgg = message.render(Context(context))

        bot.send_message(chat_id, text=msgg)

def notification_message(organization, chat_id):

    template = TelegramNotificationTemplate.objects.filter(name="Mensaje de notificación").first()
    message = Template(template.description)
    msgg = message.render(Context({'organization':organization}))
    bot.send_message(chat_id, msgg)