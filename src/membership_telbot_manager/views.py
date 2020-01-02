from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect

# Create your views here.
from telebot import types

from membership_manager.models import Organization, Invoice
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
        # bot.send_message(adminGroupID, update)
        bot.process_new_updates([update])
        return JsonResponse({'code': 200})

@bot.message_handler(commands=['ayuda', 'help'])
def help(message):
    chat_id = message.chat.id
    #help_dialog = open("telbot_intructions/help_dialog.txt", 'r')
    bot.send_message(chat_id,reply_to_message_id=message.message_id,text=f"Los comandos disponibles son los siguientes: \n 1./estado\n 2./membresias")

@bot.message_handler(commands=['estado','state'])
def state(message):
    chat_id = message.chat.id

    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        memberships = Invoice.objects.filter(
            Q(membership__state='active') | Q(membership__state='graceperiod'),
            membership__organization__telgroup__pk=telgroup.pk,
            status='pending')
        if memberships:
            new_text = "Facturas:\n"
            for inv in memberships:
                new_text+= f"{inv.membership.name}({inv.membership.state}) | " \
                           f"Expira: {inv.expiration_date.date()} Estado: {inv.status} " \
                           f"Monto: {inv.currency} {inv.amount}\n"
        else:
            new_text = "No cuenta con facturas pendientes.\n"
            memberships = Invoice.objects.filter(
                Q(membership__state='active') | Q(membership__state='inactive'),
                membership__organization__telgroup__pk=telgroup.pk,
                status='paid').order_by("payment_date").last()
            if memberships:
                for inv in memberships:
                    new_text += f"{inv.membership.name}({inv.membership.state}) | " \
                                f"Fecha de Pago: {inv.payment_date.date()} Estado: {inv.status} " \
                                f"Monto: {inv.currency} {inv.amount}\n"

        bot.send_message(chat_id, reply_to_message_id=message.message_id,text=new_text)

@bot.message_handler(commands=['membresias','memberships'])
def memberships_list(message):
    chat_id = message.chat.id
    telgroup = TelGroup.objects.filter(chat_id=message.chat.id).first()
    if telgroup:
        memberships = telgroup.organization.membs.all()
        if memberships:
            new_text = "Membresias:\n"
            for mem in memberships:
                new_text+= f"Nombre:{mem.name} - " \
                           f"Estado: {mem.state} - " \
                           f"Costo Anual: {mem.annual_cost}\n"
        else:
            new_text = "No cuenta con membresias.\n"
        bot.send_message(chat_id, reply_to_message_id=message.message_id,text=new_text)

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
    if staff_authentication(message.from_user.id):
        TelGroup.objects.create(chat_id=message.chat.id,title=message.chat.title)
        bot.send_message(adminGroupID, f'Group {message.chat.title} added, Successfully!.')
        bot.send_message(message.chat.id, f'Group {message.chat.title} added, Successfully!.')
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
    else:
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
    if telgroup :
        # telgroup.organization = org
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

def send_invoice_message(chat_id,doc):
    bot.send_document(chat_id, doc)

def send_notification_message(chat_id,organization):
    notification_message = f'Pago pentiende: Estimado {organization.contact.first_name}' \
                           f'\n'\
                           f'\t Por este medio se le recuerda que su membresía está proxima a vencer y tiene un pendiente de pago.'\
                           f'Sería una pena para Código Sur no poder renovar nuestros servicios, por favor evite esta situación cancelando'\
                           f'su deuda antes de la fecha límite.'\
                           f'\n'\
                           f'Gracias por seguir con nosotros.'\
                           F'Codigo Sur'

    bot.send_message(chat_id, notification_message)

def send_deactivated_message(chat_id,organization):
    notification_message = f'Mebresia Expirada: Estimado {organization.contact.first_name}' \
                           f'\n'\
                           f'\t Su membresía ha sido desactivada! \n'\
                           f'Se le informa que el tiempo regular de pago de su factura ha expirado, al igual que el'\
                           f'tiempo de gracia que se le otorga a nuestros clientes como voto de confianza. Nos hemos'\
                           f'visto obligados a suspenderle nuestros servicios hasta que su pago sea efectuado.' \
                           f'\n' \
                           f'Por favor asegurese cancelar su factura y reactivar su membresia.\n'\
                           f'\n'\
                           f'Más información: \n'\
                           f'Tel: +506 8569 1676 \t Correo:ayuda@codigosur.org' \
                           f'\n' \
                           f'Codigo Sur'

    bot.send_message(chat_id, notification_message)
