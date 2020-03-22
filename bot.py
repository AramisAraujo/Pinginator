import telebot
from pymongo import MongoClient
import os

if 'BOT_TOKEN' not in os.environ or 'BOT_LOGIN' not in os.environ or 'BOT_NAME' not in os.environ:
    print("Ajuste as variáveis de ambiente: BOT_TOKEN, BOT_LOGIN, BOT_NAME")
    exit(0)

TOKEN = os.environ['BOT_TOKEN']
LOGIN = os.environ['BOT_LOGIN']
NAME = os.environ['BOT_NAME']
client = MongoClient(os.environ['MONGODB_URI'])
groups = client.get_default_database()
bot = telebot.TeleBot(TOKEN)


def insert_user(message, user=None):
    user = message.from_user if user is None else user
    if message.chat.type != 'private' and not user.is_bot:
        groups[str(message.chat.id)].update_one({'name': user.username},
                                                {'$set': {'name': user.username}}, True)


@bot.message_handler(commands=['ping', 'all'])
def text_handler(message):
    chat_id = message.chat.id
    is_private = message.chat.type == 'private'
    if is_private:
        bot.send_message(chat_id, 'Só funciono em grupos :C')
    else:
        text = ''
        users = groups[str(message.chat.id)].find({})
        for user in users:
            if user['name'] != message.from_user.username:
                text += '@' + user['name'] + ' '
        if len(text) > 0:
            bot.send_message(message.chat.id, text)
    insert_user(message)


@bot.message_handler(commands=['start', 'help'])
def start_handler(message):
    bot.send_message(message.chat.id, 'Olá ' + message.from_user.first_name + ', sou ' + NAME + '.\n'
                                      'Irei chamar todos do grupo caso utilize /ping ou /all\n' +
                                      ('Funciono apenas em grupos.' if message.chat.type == 'private' else ''))
    insert_user(message)


@bot.message_handler(content_types=["new_chat_members"])
def handler_new_member(message):
    insert_user(message, message.new_chat_member)


@bot.message_handler(content_types=["left_chat_member"])
def handler_left_member(message):
    groups[str(message.chat.id)].delete_many({'name': message.left_chat_member.username})


@bot.message_handler(content_types=["text"])
def handler_text(message):
    if '@' + LOGIN in message.text:
        bot.send_message(message.chat.id, '@' + message.from_user.username)
    elif NAME in message.text:
        bot.send_message(message.chat.id, 'Am I joke to you?')
    insert_user(message)


bot.polling()

