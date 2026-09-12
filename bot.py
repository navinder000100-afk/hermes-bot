import os
import time
import requests
import threading
from flask import Flask
import telebot
from google import genai

# Environment variables fetch kar rahe hain
BOT_TOKEN = os.getenv("BOT_TOKEN", "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE")
GROUP_ID = os.getenv("GROUP_ID", "-1004429254980")
ADMIN_ID = os.getenv("ADMIN_ID", "8104262282")
UPI_ID = os.getenv("UPI_ID", "navinder000100@oksbi")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Telegram bot aur Gemini client initialize kar rahe hain
bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# Render ke liye Flask Web Server (Port error hatane ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes AI Bot is active and running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# Job scraping aur broadcasting ka main function
def job_scraper_loop():
    print("Job scraper background loop started...")
    while True:
        try:
            # Yahan tera Upwork, Reddit aur Twitter scraping ka logic aayega
            # Example ke taur par, agar koi lead milti hai toh use group par bhej sakte ho:
            # bot.send_message(GROUP_ID, "New Job Lead Found: ...")
            pass
        except Exception as e:
            print(f"Error in scraping loop: {e}")
        
        # Har 5 ya 10 minute baad check karega
        time.sleep(300)

if __name__ == "__main__":
    # 1. Flask server ko background thread mein chalao
    threading.Thread(target=run_flask, daemon=True).start()
    
    # 2. Job scraper loop ko background thread mein chalao
    threading.Thread(target=job_scraper_loop, daemon=True).start()
    
    # 3. Telegram bot ki polling start karo
    print("Starting Telegram bot polling...")
    bot.infinity_polling()
    
