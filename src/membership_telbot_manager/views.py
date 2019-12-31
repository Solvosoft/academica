from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

# Create your views here.
from telebot import types

from membership_telbot_manager.models import TelGroup, TelegramUser

def create_membership_contact_by_template(request):
    messages.error(request, "Sorry data is not valid")
    return redirect(request.META['HTTP_REFERER'])

from django.http import JsonResponse
from django.views.generic.base import View
import telebot

bot = telebot.TeleBot('926661407:AAH_pSgLYwqzSYMtspC-nU8CoY_K_kmdmCY')
bot.set_webhook(url="https://02f1ffd3.ngrok.io/telbot/")
user_dict = {}
adminGroupID = '-1001485781572'

def staff_authentication(user_id):
    teluser = TelegramUser.objects.filter(telegram_id=user_id).first()
    if teluser.user.is_staff:
        return True
    return False

class UpdateBot(View):
    def post(self, request, *args, **kwargs):
        json_string = request.body.decode("UTF-8")
        update = telebot.types.Update.de_json(json_string)
        bot.send_message(adminGroupID, update)
        bot.process_new_updates([update])
        return JsonResponse({'code': 200})

@bot.message_handler(commands=['start', 'login'])
def login(message):
    markup = types.ForceReply(selective=False)
    msg = bot.send_message(message.chat.id, "Por favor, ingresa tu usuario:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_username_step)

@bot.message_handler(commands=['salir'])
def salir(message):
    try:
        markup = types.ReplyKeyboardRemove(selective=False)
        chat_id = message.chat.id
        option = message.text
        user_dict['option'] = option
        bot.send_message(chat_id, f'Saliendo del menu... ', reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, 'Ha ocurrido un error.')

@bot.message_handler(commands=['notificaciones'])
def notifications(message):
    chat_id = message.chat.id
    # data = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('activar')
    itembtn2 = types.KeyboardButton('/salir')
    markup.add(itembtn1, itembtn2)
    msg = bot.send_message(chat_id, 'Selecciona una opción: ', reply_markup=markup)

def process_username_step(message):
    try:
        username = message.text
        user_dict['username'] = username
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, "Ahora por favor, ingresa tu contraseña:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_password_step)
    except Exception as e:
        bot.reply_to(message, 'Haocurrido algo.')

def process_password_step(message):
    try:
        chat_id = message.chat.id
        password = message.text
        user_dict['password'] = password
        user = authenticate(username=user_dict['username'], password=user_dict['password'])
        if user is not None:
            bot.send_message(message.chat.id, "Has iniciado sesión satisfactoriamente.")
            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtn1 = types.KeyboardButton('/notificaciones')
            itembtn2 = types.KeyboardButton('/salir')
            markup.add(itembtn1, itembtn2)
            msg = bot.send_message(chat_id, 'Selecciona una opción: ', reply_markup=markup)
        else:
            msg = bot.send_message(message.chat.id, "Usuario o contraseña incorrectos.")
    except Exception as e:
        bot.reply_to(message, 'Has ingresado datos incorrectos.')

@bot.message_handler(content_types=['migrate_to_chat_id'])
def group_migration(message):
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        telgroup.chat_id = message.migrate_to_chat_id
        telgroup.save()
        bot.send_message(message.migrate_to_chat_id, f'Group {message.chat.title} updated!!.')
        bot.send_message(adminGroupID, f'Group {message.chat.title} migrated from old_id {message.chat.id} to [{message.migrate_to_chat_id}].')
    else:
        bot.send_message(adminGroupID, f'The migration of chat {message.chat.id} FAils! THIS CHAT DOESNT EXIST!.')

@bot.message_handler(content_types=['group_chat_created'])
def group_creation(message):
    bot.send_message(adminGroupID, message)
    if staff_authentication(message.from_user.id):
        TelGroup.objects.create(chat_id=message.chat.id,title=message.chat.title)
        bot.send_message(adminGroupID, f'Group {message.chat.title} added, Successfully!.')
        bot.send_message(message.chat.id, f'Group {message.chat.title} added, Successfully!.')
        markup = types.ForceReply(selective=False)
        msg = bot.send_message(message.chat.id, "Pega aquí el link para compartir el grupo:", reply_markup=markup)
        bot.register_next_step_handler(msg, save_group_share_link)
    else:
        bot.send_message(message.chat.id, f'Bad operation.')

@bot.message_handler(content_types=['new_chat_members'])
def new_chat_member(message):
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        teluser = TelegramUser.objects.create(group=telgroup,telegram_id=message.from_user.id,
                                              first_name=message.from_user.first_name,
                                              last_name=message.from_user.last_name,
                                              username=message.from_user.username)
        bot.send_message(adminGroupID,
                         f'User {teluser.first_name} was resgistered, successfully!.')
        bot.send_message(message.chat.id,
                         f'User {teluser.first_name} {teluser.last_name}  was resgistered to the group '
                                          f'{telgroup.title}, successfully!.')
    bot.send_message(message.chat.id, f'This groups has no permissions')

@bot.message_handler(content_types=['left_chat_member'])
def left_chat_member(message):
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        teluser = TelegramUser.objects.filter(telegram_id=message.from_user.id,group__chat_id=telgroup.chat_id).first()
        if teluser:
            teluser.delete()
            bot.send_message(str(telgroup.chat_id),
                             f'User {teluser.first_name} was removed from {telgroup.title}, successfully!.')
            bot.send_message(adminGroupID,
                             f'User {teluser.first_name} was removed from {telgroup.title}, successfully!.')
    bot.send_message(message.chat.id, f'This groups has no permissions')

def save_group_share_link(message):
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        telgroup.invite_link = message.text
        telgroup.save()
        bot.send_message(message.chat.id, f'Invite url updated!.')

def send_invoice_message(doc):
    bot.send_document('-302481354', doc)

def send_notification_message(chat_id,message):
    bot.send_message('-302481354', message)
