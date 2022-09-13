import telebot
import os

TOKEN = os.getenv('TOKEN')
WEBHOOK = os.getenv('WEBHOOK')

bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()
bot.set_webhook(WEBHOOK)
