import os
import time
import requests
import telebot
from google import genai

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE")
GROUP_ID = os.getenv("GROUP_ID", "-1004429254980")
ADMIN_ID = os.getenv("ADMIN_ID", "8104262282")
UPI_ID = os.getenv("UPI_ID", "navinder000100@oksbi")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hermes AI Job Scraper is active!")

def job_scraper_loop():
    while True:
        try:
            # Tera scraping logic yahan rahega
            print("Scanning for jobs...")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(300)

if __name__ == "__main__":
    import threading
    # Scraper ko background thread mein chalao
    threading.Thread(target=job_scraper_loop, daemon=True).start()
    
    print("Bot polling starting...")
    bot.infinity_polling()
    
