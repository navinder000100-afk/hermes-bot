import os
import time
import threading
import telebot
from google import genai

TELEGRAM_TOKEN = "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ADMIN_ID = 8104262282

UPI_ID = "navinder000100@oksbi"
AMOUNT = "299"
PAYMENT_QR_URL = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=HermesAI%26am={AMOUNT}%26cu=INR"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)
USERS_FILE = "users.txt"

def save_chat_id(chat_id):
    chat_id_str = str(chat_id)
    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
    if chat_id_str not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{chat_id_str}\n")

# --- BACKGROUND LEAD SCRAPER ---
def run_lead_scraper():
    print("🚀 Background Lead Scraper Started...")
    while True:
        try:
            # Yahan apna scraping ka code likhein
            time.sleep(1800)
        except Exception as e:
            print(f"Scraper Error: {e}")
            time.sleep(60)

# --- TELEGRAM BOT HANDLERS ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    save_chat_id(message.chat.id)
    welcome_msg = (
        "🤖 **Welcome to Hermes AI Freelance Agent!**\n\n"
        "I can build custom Python Web Scrapers, Automation Scripts, and Fix Code Bugs instantly.\n\n"
        "📌 **How it works:**\n"
        "1. Describe your script/automation requirement in detail.\n"
        "2. Get an instant payment request of ₹299.\n"
        "3. Pay & receive fully optimized, executable Python code immediately!"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ **Access Denied!**")
        return
    promo_text = message.text.replace("/broadcast", "").strip()
    if not promo_text or not os.path.exists(USERS_FILE):
        bot.reply_to(message, "⚠️ Usage: `/broadcast Your message`", parse_mode="Markdown")
        return
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    success = 0
    for user_id in users:
        try:
            bot.send_message(user_id, promo_text, parse_mode="Markdown")
            success += 1
        except Exception:
            pass
    bot.reply_to(message, f"✅ Broadcast Complete! Sent to: {success}")

@bot.message_handler(func=lambda message: True)
def handle_incoming_messages(message):
    save_chat_id(message.chat.id)
    text = message.text.lower()
    if any(k in text for k in ["utr", "paid", "payment done", "transaction", "done"]):
        bot.reply_to(message, "⏳ **Payment Received!** Generating script via Gemini AI...")
        try:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"Write a complete Python script for: '{message.text}'",
            )
            bot.reply_to(message, f"✅ **Solution:**\n\n{response.text}", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {str(e)}")
    else:
        bot.send_photo(message.chat.id, PAYMENT_QR_URL, caption=f"⚡ Pay ₹{AMOUNT} to UPI `{UPI_ID}` and reply with UTR/Paid.", parse_mode="Markdown")

def run_bot():
    print("🚀 Starting Telegram Bot Polling...")
    try:
        bot.delete_webhook()
    except Exception:
        pass
    bot.infinity_polling()

if __name__ == "__main__":
    # Start Scraper in Background Thread
    scraper_thread = threading.Thread(target=run_lead_scraper)
    scraper_thread.daemon = True
    scraper_thread.start()

    # Start Telegram Bot
    run_bot()
    
