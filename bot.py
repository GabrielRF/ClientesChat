import datetime
import telebot
import msgs
import os
from flask import Flask, request
from telebot import types, util
from pymongo import ASCENDING, MongoClient

TOKEN = os.getenv('TOKEN')
sac_channel = os.getenv('SAC_CHANNEL')
sac_group = os.getenv('SAC_GROUP')
sac_bot = os.getenv('BOT_USERNAME')
MONGO_CON = os.getenv('MONGO_CON')
LOG_DAYS = os.getenv('LOG_DAYS')
START_MSG = os.getenv('START_MSG')
RESTART_MSG = os.getenv('RESTART_MSG')
END_MSG = os.getenv('END_MSG')
NOTIFY_ADMINS = os.getenv('NOTIFY_ADMINS')
WEBHOOK = os.getenv('WEBHOOK', False)

client = MongoClient(f"{MONGO_CON}")
db = client[sac_bot]
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

bot.set_my_commands([
    telebot.types.BotCommand("/start", "Novo atendimento"),
    telebot.types.BotCommand("/tos", "Termos do serviço"),
    telebot.types.BotCommand("/ajuda", "Ajuda"),
], telebot.types.BotCommandScope('all_private_chats'))

bot.set_my_commands([
    telebot.types.BotCommand("/p", "Definir proridade"),
    telebot.types.BotCommand("/fim", "Encerrar um atendimento"),
    telebot.types.BotCommand("/fs", "Encerrar silenciosamente um atendimento"),
    telebot.types.BotCommand("/ajuda", "Ajuda"),
    telebot.types.BotCommand("/resposta", "Definir uma resposta pronta"),
    telebot.types.BotCommand("/remover", "Remover uma resposta pronta"),
    telebot.types.BotCommand("/ban", "Banir usuário"),
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
        -1: '❌',
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
    try:
        bot.edit_message_text(chat_id=sac_channel, message_id=data['channel_thread'], text=msg, parse_mode='HTML')
    except:
        pass

def add_user_db(message):
    first_name = str(message.from_user.first_name).replace('None', '')
    last_name = str(message.from_user.last_name).replace('None', '')
    return db.users.insert_one({
        'user_id': message.from_user.id,
        'name': f'{first_name} {last_name}',
        'priority': 1,
    })

def update_user_info(user_id, key, arg):
    try:
        arg = arg.replace('None', '')
    except AttributeError:
        pass
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

def add_quick_answer(message):
    return db.answers.insert_one({
        'message': str(message),
    })

def del_quick_answer(message):
    result = db.answers.delete_one({
        'message': str(message),
    })
    return result.deleted_count

def inc_quick_answer(message):
    return db.metrics.update_one(
        {"message": message},
        {"$inc": {"usage": 1}},
        upsert=True,
    )

def find_quick_answer(text=None):
    if text:
        return db.answers.find({'message': {'$regex': f'(?i){text}'}})
    else:
        return db.answers.find()


def add_message(user_id, private_id, group_id, message):
    db.msgs.create_index('date', expireAfterSeconds=86400*int(LOG_DAYS))
    return db.msgs.insert_one({
        'user_id': user_id,
        'private_id': private_id,
        'group_id': group_id,
        'message': str(message),
        'date': datetime.datetime.now()
    })

@bot.message_handler(content_types=['document', 'audio', 'photo', 'animation', 'video_note', 'voice', 'sticker', 'video', 'contact'])
def documents(message):
    bot.send_chat_action(message.chat.id, 'typing')
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
        if user['priority'] == -1:
            update_user_info(user['user_id'], 'priority', -1)
        else:
            if user['priority'] == 0:
                update_user_info(user['user_id'], 'priority', 1)
            else:
                update_user_info(user['user_id'], 'priority', user['priority'])
            bot.pin_chat_message(sac_channel, user['channel_thread'], disable_notification=True)
            try:
                update_thread(user['user_id'])
            except:
                pass

@bot.message_handler(content_types=['pinned_message'])
@bot.channel_post_handler(content_types=['pinned_message'])
def on_pin(message):
    if int(NOTIFY_ADMINS):
        name = message.pinned_message.text
        url = f"tg:privatepost?channel={sac_channel.replace('-100', '')}&post={message.pinned_message.message_id}"
        for admin in bot.get_chat_administrators(sac_channel):
            try:
                bot.send_message(admin.user.id, msgs.pinned_msg.format(url, name), parse_mode='HTML')
            except:
                pass
    bot.delete_message(sac_channel, message.message_id)

@bot.message_handler(commands=['ajuda', 'help'])
def help(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if is_team_member(message.from_user.id):
        try:
            bot.send_message(sac_group, msgs.help_operator, parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
        except:
            bot.reply_to(message, msgs.help_user, parse_mode='HTML')
    else:
        bot.reply_to(message, msgs.help_user, parse_mode='HTML')

@bot.message_handler(commands=['fim'])
def unpin(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not is_team_member(message.from_user.id):
        return
    bot.unpin_chat_message(sac_channel, message.json['reply_to_message']['forward_from_message_id'])
    try:
        user_id = search_thread(message.reply_to_message.message_id)['user_id']
        update_user_info(user_id, 'priority', 0)
        try:
            update_thread(user_id)
        except:
            pass
        bot.send_message(sac_group, msgs.end_operator.format(message.from_user.id, message.from_user.first_name, message.from_user.last_name), parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
        bot.send_message(user_id, END_MSG.replace('<br>', '\n'), parse_mode='HTML')
    except:
        pass
    bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(commands=['fs'])
def quiet_unpin(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not is_team_member(message.from_user.id):
        return
    bot.unpin_chat_message(sac_channel, message.json['reply_to_message']['forward_from_message_id'])
    try:
        user_id = search_thread(message.reply_to_message.message_id)['user_id']
        update_user_info(user_id, 'priority', 0)
        try:
            update_thread(user_id)
        except:
            pass
        bot.send_message(sac_group, msgs.end_operator.format(message.from_user.id, message.from_user.first_name, message.from_user.last_name), parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
    except:
        pass
    bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(commands=['ban'])
def ban(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not is_team_member(message.from_user.id):
        return
    bot.unpin_chat_message(sac_channel, message.json['reply_to_message']['forward_from_message_id'])
    user_id = message.reply_to_message.json['entities'][0]['user']['id']
    try:
        update_user_info(user_id, 'priority', -1)
        try:
            update_thread(user_id)
        except:
            pass
        bot.send_message(sac_group, msgs.ban_operator.format(message.from_user.id, message.from_user.first_name, message.from_user.last_name), parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
    except:
        pass
    bot.delete_message(message.chat.id, message.message_id)

@bot.message_handler(commands=['p'])
def set_priority(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if is_team_member(message.from_user.id):
        channel_thread = message.json['reply_to_message']['message_id']
        user = search_thread(channel_thread)
        if len(message.text.split(' ')) > 1:
            priority = message.text.split()[-1]
            try:
                if 1 <= int(priority) <= 5:
                    try:
                        update_user_info(user['user_id'], 'priority', int(priority))
                        msg = update_thread(user['user_id'])
                        bot.send_message(sac_group, msgs.changed_priority, parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
                    except:
                        pass
                    bot.delete_message(message.chat.id, message.message_id)
                    return
            except ValueError:
                pass
        bot.send_message(sac_group, msgs.set_priority, parse_mode='HTML', disable_notification=True, reply_to_message_id=message.reply_to_message.message_id)

@bot.message_handler(commands=['tos'])
def tos(message):
    bot.send_chat_action(message.chat.id, 'typing')
    bot.reply_to(message, msgs.tos, parse_mode='HTML')

@bot.message_handler(commands=['start'])
def cmd_start(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if not is_team_member(message.from_user.id):
        user = search_user(message.from_user.id)
        if not user:
            add_user_db(message)
            msg = bot.send_message(sac_channel, msgs.topic_format.format(get_priority(0), message.from_user.id, message.from_user.first_name, message.from_user.last_name), parse_mode='HTML', disable_notification=True)
            add_user_thread(message.from_user.id, msg.message_id)
            user = search_user(message.from_user.id)
        bot.reply_to(message, START_MSG.format(message.from_user.first_name).replace('<br>', '\n'), parse_mode='HTML')
        if ' ' in message.text:
            start_param = message.text.replace('/start ', '')
            bot.send_message(sac_group, msgs.from_source.format(start_param), reply_to_message_id=user['thread_id'], parse_mode='HTML')
    else:
        bot.send_message(message.from_user.id, msgs.start_operator, parse_mode='HTML')

def quick_answer_save(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if is_team_member(message.from_user.id):
        if '/cancelar' in message.text:
            try:
                msg = bot.send_message(sac_group, msgs.quick_answer_error, parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
            except:
                msg = bot.send_message(message.chat.id, msgs.quick_answer_error, parse_mode='HTML')
            return
        add_quick_answer(message.text)
        try:
            msg = bot.send_message(sac_group, msgs.quick_answer_saved, parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
        except:
            msg = bot.send_message(message.chat.id, msgs.quick_answer_saved, parse_mode='HTML')


@bot.message_handler(commands=['resposta'])
def quick_answer(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if is_team_member(message.from_user.id):
        try:
            msg = bot.send_message(sac_group, msgs.quick_answer_ask, parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
        except:
            msg = bot.send_message(message.chat.id, msgs.quick_answer_ask, parse_mode='HTML')
        bot.register_next_step_handler(msg, quick_answer_save)

def quick_answer_deleted(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if is_team_member(message.from_user.id):
        answer = message.text
        answer = del_quick_answer(answer)
        if int(answer):
            msg = bot.send_message(sac_group, msgs.quick_answer_deleted, parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
        else:
            msg = bot.send_message(sac_group, msgs.quick_answer_error, parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)

@bot.message_handler(commands=['remover'])
def quick_answer_del(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if is_team_member(message.from_user.id):
        msg = bot.send_message(sac_group, msgs.quick_answer_del, parse_mode='HTML', reply_to_message_id=message.reply_to_message.message_id)
        bot.register_next_step_handler(msg, quick_answer_deleted)

@bot.message_handler(func=lambda m:True)
def on_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.from_user.id == 777000 and '👤' in message.text and '⬜️' in message.text:
        channel_thread = search_thread(message.forward_from_message_id)['thread_id']
        group_thread = message.message_id
        convert_thread(channel_thread, group_thread)
    if message.from_user.id > 777000 and not is_team_member(message.from_user.id):
        try:
            user = search_message('private_id', message.reply_to_message.message_id)
            reply_id = user['group_id']
            msg = bot.copy_message(sac_group, message.from_user.id, message.message_id, reply_to_message_id=reply_id)
        except:
            try:
                user = search_user(message.from_user.id)
                update_user_info(user['user_id'], 'name', f'{message.from_user.first_name} {message.from_user.last_name}')
            except:
                cmd_start(message)
                return
            update_thread(user['user_id'])
            user = search_user(message.from_user.id)
            reply_id = user['thread_id']
            channel_thread = user['channel_thread']
            if user['priority'] == -1:
                update_user_info(user['user_id'], 'priority', -1)
            else:
                try:
                    if user['priority'] == 0:
                        update_user_info(user['user_id'], 'priority', 1)
                        bot.send_message(user['user_id'], RESTART_MSG.replace('<br>', '\n'), parse_mode='HTML')
                    else:
                        update_user_info(user['user_id'], 'priority', user['priority'])
                    bot.pin_chat_message(sac_channel, channel_thread, disable_notification=True)
                    update_thread(user['user_id'])
                    msg = bot.copy_message(sac_group, message.from_user.id, message.message_id, reply_to_message_id=reply_id)
                except:
                    update_user_info(message.from_user.id, 'user_id', f"-{message.from_user.id}")
                    cmd_start(message)
                    return
        add_message(message.from_user.id, message.message_id, msg.message_id, message)
    if message.from_user.id > 777000 and is_team_member(message.from_user.id):
        try:
            if '#' == message.text[0]:
                return
            if search_thread(message.reply_to_message.message_id):
                reply_id = search_thread(message.reply_to_message.message_id)
                msg = bot.copy_message(reply_id['user_id'], message.chat.id, message.message_id, reply_to_message_id=reply_id)
            else:
                reply_id = search_message('group_id', message.reply_to_message.message_id)
                msg = bot.copy_message(reply_id['user_id'], message.chat.id, message.message_id, reply_to_message_id=reply_id['private_id'])
            add_message(reply_id['user_id'], msg.message_id, message.message_id, msg)
        except AttributeError:
            bot.reply_to(message, msgs.error_operator)
        except:
            bot.reply_to(message, msgs.bot_banned)
            bot.unpin_chat_message(sac_channel, message.json['reply_to_message']['forward_from_message_id'])
            update_user_info(reply_id['user_id'], 'priority', -1)
            try:
                update_thread(reply_id['user_id'])
            except:
                pass

@bot.edited_message_handler(func=lambda m:True)
def on_edit(message):
    bot.send_chat_action(message.chat.id, 'typing')
    if message.chat.id == sac_group:
        return
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
    if message.chat.type == 'channel':
        return
    if message.new_chat_member.status == 'member':
        bot.ban_chat_member(message.chat.id, message.new_chat_member.user.id)
        bot.unban_chat_member(message.chat.id, message.new_chat_member.user.id)

@bot.inline_handler(func=lambda m: True)
def query_text(query):
    if not is_team_member(query.from_user.id):
        query_result = types.InlineQueryResultArticle(0, f'@{sac_bot}', types.InputTextMessageContent(msgs.inline_user_link.format(sac_bot)))
        bot.answer_inline_query(query.id, [query_result], is_personal=True, switch_pm_text=msgs.inline_user_header, switch_pm_parameter='start')
    else:
        answers = find_quick_answer(query.query)
        query_result = []
        for i, answer in enumerate(answers[:25]):
            query_result.append(types.InlineQueryResultArticle(i, answer['message'], types.InputTextMessageContent(answer['message'], parse_mode='Markdown', disable_web_page_preview=True)))
        bot.answer_inline_query(query.id, query_result, cache_time=120)

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    if not WEBHOOK:
        bot.polling(allowed_updates=telebot.util.update_types)
    else:
        bot.set_webhook(url=WEBHOOK + TOKEN)
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
