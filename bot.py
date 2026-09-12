import os
from flask import Flask
import threading
import telebot

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Flask ko alag thread me chalao taaki bot polling na ruke
threading.Thread(target=run_flask, daemon=True).start()

# Telegram Bot Setup
BOT_TOKEN = os.getenv("BOT_TOKEN", "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hermes AI is active!")

# Bot polling start karo
bot.infinity_polling()
