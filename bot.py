import os
import threading
from flask import Flask
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hermes AI is active and running!")

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Purane webhook aur conflict ko hatane ke liye yeh line daal
    bot.remove_webhook()
    
    print("Starting Telegram bot polling...")
    bot.infinity_polling(skip_pending=True)
    
