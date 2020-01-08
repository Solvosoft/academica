from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect

# Create your views here.
from django.template.loader import render_to_string
from telebot import types
from django.http import JsonResponse
from django.views.generic.base import View
from membership_manager.models import Organization, Invoice
from membership_telbot_manager.models import TelGroup, TelegramUser
import telebot
from django.conf import settings


def create_membership_contact_by_template(request):
    messages.error(request, "Sorry data is not valid")
    return redirect(request.META['HTTP_REFERER'])


bot = telebot.TeleBot(settings.TELEGRAM_BOT_API)
bot.set_webhook(url=settings.TELEGRAM_BOT_WEBHOOK)
user_dict = {}
adminGroupID = settings.TELEGRAM_ADMIN_GROUP_ID


def staff_authentication(user_id):
    teluser = TelegramUser.objects.filter(telegram_id=user_id).first()
    if teluser.user.is_staff:
        return True
    return False


class UpdateBot(View):
    def post(self, request, *args, **kwargs):
        json_string = request.body.decode("UTF-8")
        update = telebot.types.Update.de_json(json_string)
        # bot.send_message(adminGroupID, update)
        bot.process_new_updates([update])
        return JsonResponse({'code': 200})


@bot.message_handler(commands=['ayuda', 'help'])
def help(message):
    chat_id = message.chat.id
    rendered = render_to_string('help_dialog.txt')
    bot.send_message(chat_id, reply_to_message_id=message.message_id, text=rendered)


@bot.message_handler(commands=['estado', 'state', 'ESTADO', 'STATE'])
def state(message):
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
                                    {'invoice': invoices, 'option': "pagas", 'title': invoices.membership.name})

        bot.send_message(chat_id, reply_to_message_id=message.message_id, text=msgg)


@bot.message_handler(commands=['membresias', 'memberships'])
def memberships_list(message):
    chat_id = message.chat.id
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        memberships = telgroup.organization.membs.all()
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
    chat_id = message.chat.id
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        memberships = telgroup.organization.membs.filter(state='active')
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
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        telgroup.chat_id = message.migrate_to_chat_id
        telgroup.save()
        bot.send_message(message.migrate_to_chat_id, f'Group {message.chat.title} updated!!.')
        bot.send_message(adminGroupID,
                         f'Group {message.chat.title} migrated from old_id {message.chat.id} to [{message.migrate_to_chat_id}].')
    else:
        bot.send_message(adminGroupID, f'The migration of chat {message.chat.id} FAils! THIS CHAT DOESNT EXIST!.')


@bot.message_handler(content_types=['group_chat_created'])
def group_creation(message):
    if staff_authentication(message.from_user.id):
        TelGroup.objects.create(chat_id=message.chat.id, title=message.chat.title)
        bot.send_message(adminGroupID, f'Group {message.chat.title} added, Successfully!.')
        bot.send_message(message.chat.id, f'Group {message.chat.title} added, Successfully!.')
    else:
        bot.send_message(message.chat.id, f'Bad operation.')


@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        teluser = TelegramUser.objects.filter(telegram_id=message.from_user.id).first()
        if teluser and not telgroup.telegramuser_set.filter(telegram_id=teluser.telegram_id).exists():
            teluser.groups.add(telgroup)
            bot.send_message(adminGroupID,
                             f'User {teluser.first_name} added, successfully!.')
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
            bot.send_message(adminGroupID,
                             f'User {teluser.first_name} was resgistered, successfully!.')
            bot.send_message(message.chat.id,
                             f'User {teluser.first_name} {teluser.last_name}  was added to the group '
                             f'{telgroup.title}, successfully!.')
    else:
        bot.send_message(message.chat.id, f'This groups has no permissions')


@bot.message_handler(content_types=['left_chat_member'])
def left_chat_member(message):
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        teluser = TelegramUser.objects.filter(telegram_id=message.from_user.id,
                                              groups__chat_id=telgroup.chat_id).first()
        if telgroup.telegramuser_set.filter(telegram_id=message.from_user.id).exists():
            telgroup.telegramuser_set.remove(teluser)
            bot.send_message(str(telgroup.chat_id),
                             f'User {teluser.first_name} was removed from {telgroup.title}, successfully!.')
            bot.send_message(adminGroupID,
                             f'User {teluser.first_name} was removed from {telgroup.title}, successfully!.')
    else:
        bot.send_message(message.chat.id, f'This groups has no permissions')


def save_group_share_link(message):
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        telgroup.invite_link = message.text
        telgroup.save()
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id,
                               "Ingresa el correo electronico de la organizacion la cual se va a enlazar con este grupo:",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, link_telgroup_orgnanization)


def link_telgroup_orgnanization(message):
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    org = Organization.objects.filter(email=message.text).first()
    if telgroup and org:
        telgroup.organization = org
        telgroup.save()
        bot.send_message(message.chat.id, f'Invite url and email updated!.')


def send_invoice_message(chat_id, doc):
    bot.send_document(chat_id, doc)


def send_notification_message(chat_id, organization):
    rendered = render_to_string('notification_message.txt', {'organization': organization})
    bot.send_message(chat_id, rendered)


def send_deactivated_message(chat_id, organization):
    rendered = render_to_string('expiration_message.txt', {'organization': organization})
    bot.send_message(chat_id, rendered)
