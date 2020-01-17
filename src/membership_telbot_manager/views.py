from time import sleep

from django.db.models import Q
from django.template.loader import render_to_string
from membership_manager.models import Organization, Invoice
from membership_telbot_manager.models import TelGroup, TelegramUser
from django.http import JsonResponse
from django.views.generic.base import View
from django.conf import settings
import telebot

bot = telebot.TeleBot(settings.TELEGRAM_BOT_API)
sleep(2)
bot.set_webhook(url=settings.TELEGRAM_BOT_WEBHOOK)


def staff_authentication(user_id):
    """
    Authenticator, checks if the Telegram user is registered on server. If True, then allow to do soemthing.
    Is just for authentication porpouses.

    :param user_id: Telegram user id.
    :return: True or False
    """
    teluser = TelegramUser.objects.filter(telegram_id=user_id).first()
    if teluser.user.is_staff:
        return True
    return False

#Webhook used to get TelegramBot Updates. CHANGE THIS IF NECESSARY
class UpdateBot(View):

    def post(self, request, *args, **kwargs):
        json_string = request.body.decode("UTF-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return JsonResponse({'code': 200})


@bot.message_handler(commands=['ayuda', 'help'])
def help(message):
    """
    Show up the available commands.

    :param message:
    :return:
    """
    chat_id = message.chat.id
    rendered = render_to_string('help_dialog.txt')
    bot.send_message(chat_id, reply_to_message_id=message.message_id, text=rendered)


@bot.message_handler(commands=['estado', 'state', 'ESTADO', 'STATE'])
def state(message):
    """
    Sends the Organization Invoice State.

    :param message:
    :return:
    """
    chat_id = message.chat.id
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        invoices = Invoice.objects.filter(
            Q(membership__state='active') | Q(membership__state='graceperiod'),
            membership__organization__telgroup__pk=telgroup.pk,
            status='pending')
        if invoices:
            msgg = render_to_string('invoices.txt', {'invoices': invoices, 'option': "pendientes",
                                                     'title': invoices.first().membership.name})
        else:
            invoices = Invoice.objects.filter(
                Q(membership__state='active') | Q(membership__state='inactive'),
                membership__organization__telgroup__pk=telgroup.pk,
                status='paid').order_by("payment_date").last()
            msgg = render_to_string('invoices.txt',
                                    {'invoice': invoices or [], 'option': "pagas",
                                     'title': invoices.membership.name if invoices else "Sin facturación"})

        bot.send_message(chat_id, reply_to_message_id=message.message_id, text=msgg)


@bot.message_handler(commands=['membresias', 'memberships'])
def memberships_list(message):
    """
    Sends organizations membership list.
    :param message:
    :return:
    """
    chat_id = message.chat.id
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        memberships = telgroup.organization.membership_set.all()
        if memberships:
            msgg = render_to_string('memberships.txt', {'memberships': memberships, 'option': "membresias",
                                                        'title': telgroup.organization.name})
        else:
            new_text = "No cuenta con membresias.\n"
            msgg = render_to_string('memberships.txt',
                                    {'memberships': new_text, 'option': "none", 'title': telgroup.organization.name})

        bot.send_message(chat_id, reply_to_message_id=message.message_id, text=msgg)


@bot.message_handler(commands=['services', 'servicios'])
def memberships_services_list(message):
    """
    Send Detailed Membership Services List.
    :param message:
    :return:
    """
    chat_id = message.chat.id
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        memberships = telgroup.organization.membership_set.filter(state='active')
        if memberships:
            msgg = render_to_string('memberships.txt', {'memberships': memberships, 'option': "services",
                                                        'title': telgroup.organization.name})
        else:
            new_text = "No cuenta con membresias.\n"
            msgg = render_to_string('memberships.txt',
                                    {'memberships': new_text, 'option': "none", 'title': telgroup.organization.name})

        bot.send_message(chat_id, reply_to_message_id=message.message_id, text=msgg)

@bot.message_handler(content_types=['migrate_to_chat_id'])
def group_migration(message):
    """
    Sometimes the group change to supergroup, and this event need a chat_id migration.
    keep this code.

    :param message:
    :return:
    """
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        telgroup.chat_id = message.migrate_to_chat_id
        telgroup.save()
        bot.send_message(message.migrate_to_chat_id, f'Group {message.chat.title} updated!!.')


@bot.message_handler(content_types=['group_chat_created'])
def group_creation(message):
    """
    Detects when group is created, if the user is staff , save it.
    :param message: Message Update Information, the whole information about the event executed!, received from webhook.
    :return:
    """
    if staff_authentication(message.from_user.id):
        TelGroup.objects.create(chat_id=message.chat.id,title=message.chat.title)
        bot.send_message(message.chat.id, f'Group {message.chat.title} added, Successfully!.')
    else:
        bot.send_message(message.chat.id, f'Bad operation.')


@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    """
    Handle when a new chat member is added to the group. THen link it to the chat group.
    :param message: Message Update Information, the whole information about the event executed!, received from webhook.
    :return:
    """
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        teluser = TelegramUser.objects.filter(telegram_id=message.from_user.id).first()
        if teluser and not telgroup.telegramuser_set.filter(telegram_id=teluser.telegram_id).exists():
           teluser.groups.add(telgroup)
           bot.send_message(message.chat.id,
                            f'User {teluser.first_name} {teluser.last_name}  was added to the group '
                            f'{telgroup.title}, successfully!.')
        elif not teluser:
           teluser = TelegramUser(telegram_id=message.from_user.id,
                                                  first_name=message.from_user.first_name,
                                                  last_name=message.from_user.last_name,
                                                  username=message.from_user.username)
           teluser.save()
           teluser.groups.add(telgroup)
           bot.send_message(message.chat.id,
                         f'User {teluser.first_name} {teluser.last_name}  was added to the group '
                                              f'{telgroup.title}, successfully!.')
    else:
        bot.send_message(message.chat.id, """Grupo sin permisos, por favor registre su usuario (%s) en la platafora
         y cree un grupo en la administración con este id %s"""%(str(message.from_user.id), str(message.chat.id)))


@bot.message_handler(content_types=['left_chat_member'])
def left_chat_member(message):
    """
    Check if a chat member left from chat, then remove it from group at server db.
    Message contains the information about the update from telegram bot.
    :param message: Message Update Information, the whole information about the event executed!, received from webhook.
    :return: nothing, just send a message
    """
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        teluser = TelegramUser.objects.filter(telegram_id=message.from_user.id,
                                              groups__chat_id=telgroup.chat_id).first()
        if telgroup.telegramuser_set.filter(telegram_id=message.from_user.id).exists():
            telgroup.telegramuser_set.remove(teluser)
            bot.send_message(str(telgroup.chat_id),
                             f'User {teluser.first_name} was removed from {telgroup.title}, successfully!.')
    else:
        bot.send_message(message.chat.id, f'This groups has no permissions')


def send_invoice_message(chat_id,doc):
    """
    Sends the invoice pdf file, this method is called from pay_invoice() from membershio_manager/admin_pdf.py.

    :param chat_id: Telegram chat id to send message.
    :param doc: Invoice PDF File
    :return: Nothing, sends the doc via Telegram.
    """
    bot.send_document(chat_id, doc)

def send_notification_message(chat_id,organization):
    """ This method is called from task invoice_creation() and notify_invoice_expiration().
    Used to send pending notifications

    :param chat_id: Telegram chat id to send message.
    :param organization:  Organization object, to pick up the organization info.
    :return: Nothing, Sends the notification.
    """
    rendered = render_to_string('notification_message.txt',{'organization':organization})
    bot.send_message(chat_id, rendered)

def send_deactivated_message(chat_id,organization):
    """
    This method is called from task membership_deactivating, used to send notifications via Telegram
    using chat_id and organization object.

    :param chat_id: Telegram chat id to send message.
    :param organization:  Organization object, to pick up the organization info.
    :return: Nothing, Sends the notification.
    """
    rendered = render_to_string('expiration_message.txt',{'organization':organization})
    bot.send_message(chat_id, rendered)
