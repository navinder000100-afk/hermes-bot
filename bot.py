import os
import threading
from flask import Flask
import telebot

# Telegram Bot Setup
BOT_TOKEN = os.getenv("BOT_TOKEN", "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hermes AI is active and running!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Got your message: {message.text}")

# Flask Web Server Setup (Render port requirement ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

if __name__ == "__main__":
    # Flask ko background thread mein daal diya
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask server started in background thread.")

    # Main thread mein Telegram bot polling chalegi
    print("Starting Telegram bot polling...")
    bot.infinity_polling(skip_pending=True)
    
