import os
import threading
import time
from flask import Flask
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID") # Render environment variable mein dalna hai
bot = telebot.TeleBot(BOT_TOKEN)

# Database / List for Paid Users & Admin
PAID_USERS = [] 
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789")) # Apni Telegram Numeric ID yahan ya env mein daal

def is_paid(user_id):
    return user_id in PAID_USERS or user_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if is_paid(user_id):
        welcome_text = (
            "🚀 **Hermes Ultimate Automation System Active**\n\n"
            "🔹 **Modules Loaded:**\n"
            "• Automated Lead Finder & Channel Poster\n"
            "• Dynamic Script & Code Generator\n"
            "• Background Task Processor\n\n"
            "Apna task bhej ya `/help` use kar!"
        )
    else:
        welcome_text = (
            "🔒 **System Locked**\n\n"
            "Yeh ek paid automation bot hai. Access ke liye `/pay` command use karein."
        )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['pay'])
def payment_info(message):
    pay_text = (
        "💳 **Automation License Payment**\n\n"
        "Full access ke liye payment karein:\n"
        "• UPI ID: `yourname@upi`\n"
        "Payment ke baad screenshot aur apni User ID admin ko bhejein."
    )
    bot.reply_to(message, pay_text, parse_mode="Markdown")

@bot.message_handler(commands=['addpaid'])
def add_paid_user(message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        try:
            target_id = int(message.text.split()[1])
            if target_id not in PAID_USERS:
                PAID_USERS.append(target_id)
                bot.reply_to(message, f"Success! User `{target_id}` ko system access mil gaya hai.", parse_mode="Markdown")
            else:
                bot.reply_to(message, "Yeh user pehle se authorized hai.")
        except IndexError:
            bot.reply_to(message, "Sahi format: `/addpaid <user_id>`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Aapke paas yeh command chalane ki permission nahi hai.")

# Background Auto-Scraper & Channel Poster Loop
def background_automation_loop():
    while True:
        try:
            # Yahan teri real automation / web scraping logic aayegi
            time.sleep(60) # Har 60 seconds mein check karega
            automated_lead = (
                "⚡ **Auto-Scraped Lead / Task**\n\n"
                "• Category: Automation / Scripting\n"
                "• Status: Verified & Live\n"
                "• Action Required: Check dashboard"
            )
            if CHANNEL_ID:
                bot.send_message(CHANNEL_ID, automated_lead, parse_mode="Markdown")
        except Exception as e:
            print(f"Automation loop error: {e}")
            time.sleep(10)

@bot.message_handler(func=lambda message: True)
def handle_automation_queries(message):
    user_id = message.from_user.id
    if not is_paid(user_id):
        bot.reply_to(message, "❌ Access Denied! Pehle subscription le bhai (`/pay`).")
        return

    query = message.text
    # System logic to handle scripting, automation queries, or commands
    response_text = (
        f"⚙️ **Automation Pipeline Executing:** `{query}`\n\n"
        f"```python\n"
        f"# Auto-generated system script\n"
        f"import requests\n\n"
        f"def run_system_task():\n"
        f"    print('Processing: {query}')\n"
        f"    # Automation steps executed successfully\n"
        f"run_system_task()\n"
        f"```"
    )
    bot.reply_to(message, response_text, parse_mode="Markdown")

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Automation Engine is running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)

if __name__ == "__main__":
    # 1. Start Flask Web Server in Background
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # 2. Start Continuous Background Automation/Scraping Loop
    auto_thread = threading.Thread(target=background_automation_loop, daemon=True)
    auto_thread.start()
    
    # 3. Clear Webhooks & Start Telegram Polling
    bot.remove_webhook()
    print("Starting Telegram bot polling & automation engine...")
    bot.infinity_polling(skip_pending=True)
                
