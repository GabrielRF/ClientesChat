import telebot
from telebot import types,util
from pymongo import ASCENDING, MongoClient

client = MongoClient()
db = client.sac
bot = telebot.TeleBot('2118150557:AAF50aifvDepZVednI4ksyvKb2hqWhVg2EQ')
sac_channel = -1001688033043
sac_group = -1001339156805

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

def add_user_db(user_id):
    return db.users.insert_one({
        'user_id': user_id,
    })

def add_user_thread(user_id, thread_id):
    return db.users.update_one(
        {'user_id': user_id},
        {'$set': {
            'thread_id': thread_id,
            'channel_thread': thread_id,
        }},
    )

def is_team_member(user_id):
    if bot.get_chat_member(sac_group, user_id).status == 'left':
        return False
    return True

def add_message(user_id, private_id, group_id, message):
    return db.msgs.insert_one({
        'user_id': user_id,
        'private_id': private_id,
        'group_id': group_id,
        'message': str(message),
    })

@bot.message_handler(content_types=['pinned_message'])
@bot.channel_post_handler(content_types=['pinned_message'])
def on_pin(message):
    bot.delete_message(sac_channel, message.message_id)

@bot.message_handler(commands=['fim'])
def unpin(message):
    bot.unpin_chat_message(sac_channel, message.json['reply_to_message']['forward_from_message_id'])
    

@bot.message_handler(func=lambda m:True)
def on_message(message):
    #print(message)
    if message.from_user.id == 777000 and '👤' in message.text and '📟' in message.text:
        channel_thread = search_thread(message.forward_from_message_id)['thread_id']
        group_thread = message.message_id
        convert_thread(channel_thread, group_thread)
        bot.pin_chat_message(sac_channel, channel_thread, disable_notification=True)
    if message.from_user.id > 777000 and not is_team_member(message.from_user.id):
        user = search_user(message.from_user.id)
        if not user:
            add_user_db(message.from_user.id)
            #msg = bot.copy_message(sac_channel, message.from_user.id, message.message_id)
            msg = bot.send_message(sac_channel, f'📟 <a href="tg://user?id={message.from_user.id}">{message.from_user.id}</a>\n👤 {message.from_user.first_name}', parse_mode='HTML')
            add_user_thread(message.from_user.id, msg.message_id)
        else:
            if message.reply_to_message:
                user = search_message('private_id', message.reply_to_message.message_id)
                reply_id = user['group_id']
            else:
                user = search_user(message.from_user.id)
                print(user)
                reply_id = user['thread_id']
                channel_thread = user['channel_thread']
                bot.pin_chat_message(sac_channel, channel_thread, disable_notification=True)
            msg = bot.send_message(sac_group, message.text, reply_to_message_id=reply_id)
        add_message(message.from_user.id, message.message_id, msg.message_id, message)
    if message.from_user.id > 777000 and is_team_member(message.from_user.id):
        if search_thread(message.reply_to_message.message_id):
            reply_id = search_thread(message.reply_to_message.message_id)
            msg = bot.send_message(reply_id['user_id'], message.text)
        else:
            reply_id = search_message('group_id', message.reply_to_message.message_id)
            msg = bot.send_message(reply_id['user_id'], message.text, reply_to_message_id=reply_id['private_id'])
        add_message(reply_id['user_id'], msg.message_id, message.message_id, msg)


@bot.edited_message_handler(func=lambda m:True)
def on_edit(message):
    if not is_team_member(message.from_user.id):
        group_id = search_message('private_id', message.json['message_id'])['group_id']
        bot.edit_message_text(message.text, sac_group, group_id)
    else:
        chat_id = search_message('group_id', message.message_id)
        bot.edit_message_text(message.text, chat_id['user_id'], chat_id['private_id'])

@bot.chat_member_handler(func=lambda m:True)
def on_chat_action(message):
    if message.new_chat_member.status == 'member':
        bot.ban_chat_member(message.chat.id, message.new_chat_member.user.id)
        bot.unban_chat_member(message.chat.id, message.new_chat_member.user.id)

bot.polling(allowed_updates=telebot.util.update_types)
