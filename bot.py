import telebot
import msgs
from telebot import types, util
from pymongo import ASCENDING, MongoClient

client = MongoClient()
db = client.sac
bot = telebot.TeleBot('2118150557:AAF50aifvDepZVednI4ksyvKb2hqWhVg2EQ')
sac_channel = -1001688033043
sac_group = -1001339156805

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Novo atendimento"),
    telebot.types.BotCommand("/tos", "Termos do serviço"),
], telebot.types.BotCommandScope('all_private_chats'))

bot.set_my_commands([
    telebot.types.BotCommand("/p", "Definir proridade"),
    telebot.types.BotCommand("/fim", "Encerrar um atendimento")
], telebot.types.BotCommandScope('all_group_chats'))

def search_user(user_id):
    return db.users.find_one({"user_id": user_id})

def search_thread(thread_id):
    return db.users.find_one({'thread_id': thread_id})

def search_message(key, arg):
    return db.msgs.find_one({key: arg})

def convert_thread(channel_thread, group_thread):
    return db.users.update_one(
        {'thread_id': channel_thread},
        {'$set': {'thread_id': group_thread}}
    )

def get_priority(value):
    cases = {
        0: '⬜️',
        1: '🟦',
        2: '🟩',
        3: '🟨',
        4: '🟧',
        5: '🟥',
    }
    return cases.get(value)

def update_thread(user_id):
    data = search_user(user_id)
    msg = msgs.topic_format.format(get_priority(data["priority"]), data["user_id"], data["name"], '')
    #msgs.topic_format.format(get_priority(1), message.from_user.id, message.from_user.first_name, message.from_user.last_name)

    return bot.edit_message_text(chat_id=sac_channel, message_id=data['channel_thread'], text=msg, parse_mode='HTML')

def add_user_db(message):
    return db.users.insert_one({
        'user_id': message.from_user.id,
        'name': f'{message.from_user.first_name} {message.from_user.last_name}',
        'priority': 1,
    })

def update_user_info(user_id, key, arg):
     return db.users.update_one(
        {'user_id': user_id},
        {'$set': {key: arg}},
    )

def add_user_thread(user_id, thread_id):
    return db.users.update_one(
        {'user_id': user_id},
        {'$set': {
            'thread_id': thread_id,
            'channel_thread': thread_id,
        }},
    )

def is_team_member(user_id):
    if bot.get_chat_member(sac_channel, user_id).status == 'left':
        return False
    return True

def add_message(user_id, private_id, group_id, message):
    return db.msgs.insert_one({
        'user_id': user_id,
        'private_id': private_id,
        'group_id': group_id,
        'message': str(message),
    })

@bot.message_handler(content_types=['document', 'audio', 'photo', 'animation', 'voice_note', 'audio', 'sticker'])
def documents(message):
    if is_team_member(message.from_user.id):
        channel_thread = message.json['reply_to_message']['message_id']
        user = search_thread(channel_thread)
        if user:
            msg = bot.copy_message(user['user_id'], sac_group, message.message_id)
        else:
            user = search_message('group_id', channel_thread)
            msg = bot.copy_message(user['user_id'], sac_group, message.message_id)
        add_message(user['user_id'], msg.message_id, message.message_id, msg)
    else:
        user = search_user(message.from_user.id)
        msg = bot.copy_message(sac_group, message.from_user.id, message.message_id, reply_to_message_id=user['thread_id'])
        add_message(message.from_user.id, message.message_id, msg.message_id, message)

@bot.message_handler(content_types=['pinned_message'])
@bot.channel_post_handler(content_types=['pinned_message'])
def on_pin(message):
    bot.delete_message(sac_channel, message.message_id)

@bot.message_handler(commands=['fim'])
def unpin(message):
    bot.unpin_chat_message(sac_channel, message.json['reply_to_message']['forward_from_message_id'])
    user_id = message.reply_to_message.json['entities'][0]['user']['id']
    try:
        update_user_info(user_id, 'priority', int(0))
        try:
            update_thread(user_id)
        except:
            pass
        bot.send_message(sac_group, msgs.end_operator.format(message.from_user.id, message.from_user.first_name, message.from_user.last_name), parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
        bot.send_message(user_id, msgs.end_user)
    except:
        pass
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['p'])
def set_priority(message):
    if is_team_member(message.from_user.id):
        if len(message.text.split(' ')) > 1:
            channel_thread = message.json['reply_to_message']['message_id']
            user = search_thread(channel_thread)
            priority = message.text.split()[-1]
            try:
                if 1 <= int(priority) <= 5:
                    try:
                        update_user_info(user['user_id'], 'priority', int(priority))
                        msg = update_thread(user['user_id'])
                    except:
                        pass
                    bot.delete_message(message.chat.id, message.message_id)
                    return
            except ValueError:
                pass
        bot.reply_to(message, msgs.set_priority, parse_mode='HTML')

@bot.message_handler(commands=['tos'])
def tos(message):
    bot.reply_to(message, msgs.tos, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.reply_to(message, msgs.start.format(message.from_user.first_name), parse_mode='HTML')

@bot.message_handler(func=lambda m:True)
def on_message(message):
    if message.from_user.id == 777000 and '👤' in message.text and '🟦' in message.text:
        channel_thread = search_thread(message.forward_from_message_id)['thread_id']
        group_thread = message.message_id
        convert_thread(channel_thread, group_thread)
        bot.pin_chat_message(sac_channel, channel_thread, disable_notification=True)
    if message.from_user.id > 777000 and not is_team_member(message.from_user.id):
        user = search_user(message.from_user.id)
        if not user:
            add_user_db(message)
            msg = bot.send_message(sac_channel, msgs.topic_format.format(get_priority(1), message.from_user.id, message.from_user.first_name, message.from_user.last_name), parse_mode='HTML')
            add_user_thread(message.from_user.id, msg.message_id)
        else:
            if message.reply_to_message:
                user = search_message('private_id', message.reply_to_message.message_id)
                reply_id = user['group_id']
            else:
                user = search_user(message.from_user.id)
                reply_id = user['thread_id']
                channel_thread = user['channel_thread']
                bot.pin_chat_message(sac_channel, channel_thread, disable_notification=True)
                try:
                    update_user_info(user['user_id'], 'priority', int(1))
                    update_thread(user['user_id'])
                except:
                    pass
            msg = bot.send_message(sac_group, message.text, reply_to_message_id=reply_id)
        add_message(message.from_user.id, message.message_id, msg.message_id, message)
    if message.from_user.id > 777000 and is_team_member(message.from_user.id):
        try:
            if search_thread(message.reply_to_message.message_id):
                reply_id = search_thread(message.reply_to_message.message_id)
                msg = bot.send_message(reply_id['user_id'], message.text)
            else:
                reply_id = search_message('group_id', message.reply_to_message.message_id)
                msg = bot.send_message(reply_id['user_id'], message.text, reply_to_message_id=reply_id['private_id'])
            add_message(reply_id['user_id'], msg.message_id, message.message_id, msg)
        except AttributeError:
            bot.reply_to(message, msgs.error_operator)


@bot.edited_message_handler(func=lambda m:True)
def on_edit(message):
    if message.from_user.id == 777000:
        return
    if not is_team_member(message.from_user.id):
        data = search_message('private_id', message.json['message_id'])
        bot.edit_message_text(message.text, sac_group, data['group_id'])
        add_message(message.from_user.id, data['private_id'], 'edit', message)
    else:
        chat_id = search_message('group_id', message.message_id)
        bot.edit_message_text(message.text, chat_id['user_id'], chat_id['private_id'])
        add_message(chat_id['user_id'], chat_id['private_id'], 'edit', message)

@bot.chat_member_handler(func=lambda m:True)
def on_chat_action(message):
    if message.new_chat_member.status == 'member':
        bot.ban_chat_member(message.chat.id, message.new_chat_member.user.id)
        bot.unban_chat_member(message.chat.id, message.new_chat_member.user.id)

bot.polling(allowed_updates=telebot.util.update_types)
