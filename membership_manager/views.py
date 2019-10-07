from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect


# Create your views here.
from telebot import types


def create_membership_contact_by_template(request):

    messages.error(request, "Sorry data is not valid")
    return redirect(request.META['HTTP_REFERER'])

from django.http import JsonResponse
from django.views.generic.base import View
import telebot

bot = telebot.TeleBot('926661407:AAH_pSgLYwqzSYMtspC-nU8CoY_K_kmdmCY')
user_dict = {}
class UpdateBot(View):
    def post(self, request, *args, **kwargs):
        json_string = request.body.decode("UTF-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return JsonResponse({'code': 200})

@bot.message_handler(commands=['start','login'])
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
    #data = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('ativar')
    itembtn2 = types.KeyboardButton('/salir')
    markup.add(itembtn1, itembtn2)
    msg = bot.send_message(chat_id, 'Selecciona una opción: ', reply_markup=markup)

def process_username_step(message):
    try:
        chat_id = message.chat.id
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


@bot.message_handler(content_types='text')
def send_Message(message):
    bot.send_message(message.chat.id,f'Replying:  {message.text} ')

