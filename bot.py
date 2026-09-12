import os
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask
import telebot
import google.generativeai as genai

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini AI with requested model
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {"temperature": 0.7, "max_output_tokens": 1500}
model = genai.GenerativeModel(model_name="gemini-3.6-flash", generation_config=generation_config)

bot = telebot.TeleBot(BOT_TOKEN)
PAID_USERS = []

def is_paid(user_id):
    return user_id in PAID_USERS or user_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_paid(message.from_user.id):
        bot.reply_to(message, "🔒 Access Denied. Use /pay for subscription.")
        return
    bot.reply_to(message, "🚀 **Hermes AI (Gemini 3.6 Powered)** is active! Koi bhi coding task, script generation, ya sawal pucho.")

@bot.message_handler(commands=['pay'])
def pay_info(message):
    bot.reply_to(message, "💳 Send payment to UPI: `yourname@upi` and share screenshot with admin for activation.")

@bot.message_handler(commands=['addpaid'])
def add_paid(message):
    if message.from_user.id == ADMIN_ID:
        try:
            uid = int(message.text.split()[1])
            if uid not in PAID_USERS:
                PAID_USERS.append(uid)
            bot.reply_to(message, f"Success! User `{uid}` ko access mil gaya hai.", parse_mode="Markdown")
        except:
            bot.reply_to(message, "Sahi format: `/addpaid <user_id>`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Permission denied.")

def background_lead_scraper():
    while True:
        try:
            time.sleep(60)
            if CHANNEL_ID:
                live_lead = "🔥 **Live Scraped Lead / Alert**\n\n• Source: Target API/Site\n• Status: Active & Verified"
                bot.send_message(CHANNEL_ID, live_lead, parse_mode="Markdown")
        except Exception as e:
            print(f"Scraper error: {e}")
            time.sleep(10)

@bot.message_handler(func=lambda message: True)
def handle_ai_and_scraping(message):
    if not is_paid(message.from_user.id):
        bot.reply_to(message, "❌ Pehle subscription le bhai! (`/pay`)", parse_mode="Markdown")
        return
    
    query = message.text.strip()
    
    if query.startswith("http://") or query.startswith("https://"):
        try:
            res = requests.get(query, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(res.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No Title Found"
            bot.reply_to(message, f"🌐 **Scraped Webpage Data:**\n• URL: `{query}`\n• Page Title: *{title}*", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ Scraping Error: `{e}`", parse_mode="Markdown")
    else:
        try:
            response = model.generate_content(query)
            ai_reply = response.text
            
            if len(ai_reply) > 4000:
                ai_reply = ai_reply[:4000] + "\n\n*(Truncated due to length)*"
                
            bot.reply_to(message, ai_reply, parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ AI Generation Error: `{e}`")

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Gemini Engine is live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    scraper_thread = threading.Thread(target=background_lead_scraper, daemon=True)
    scraper_thread.start()
    
    bot.remove_webhook()
    print("Starting Gemini Telegram bot polling...")
    bot.infinity_polling(skip_pending=True)
    
