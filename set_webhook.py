import telebot
import sys

TOKEN = sys.argv[1]
WEBHOOK = sys.argv[2]

bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()
bot.set_webhook(WEBHOOK)
