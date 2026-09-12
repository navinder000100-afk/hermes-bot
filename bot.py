import os
import time
import threading
import telebot
from flask import Flask
from google import genai

TELEGRAM_TOKEN = "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ADMIN_ID = 8104262282

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

USERS_FILE = "users.txt"

@app.route('/')
def home():
    return "Hermes Bot & Scraper active!"

# --- YAHAN APNA SCRAPER CODE DALEN (Background Loop) ---
def run_lead_scraper():
    print("🚀 Background Lead Scraper Started...")
    while True:
        try:
            # Apni scraping ka logic yahan likhein (jaise website request, parsing, etc.)
            # Example: 
            # leads = fetch_leads_from_website()
            # save_leads(leads)
            
            # Har 30 ya 60 minute baad run karne ke liye delay
            time.sleep(1800) 
        except Exception as e:
            print(f"Scraper Error: {e}")
            time.sleep(60)

# --- TELEGRAM BOT POLLING ---
def run_bot():
    bot.delete_webhook()
    bot.infinity_polling()

if __name__ == "__main__":
    # 1. Scraper Thread Start Karein
    scraper_thread = threading.Thread(target=run_lead_scraper)
    scraper_thread.daemon = True
    scraper_thread.start()

    # 2. Telegram Bot Thread Start Karein
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # 3. Flask Server (Render Port Binding ke liye)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
