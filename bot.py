import os
import time
import threading
import requests
import telebot
from google import genai

TELEGRAM_TOKEN = "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ADMIN_ID = 8104262282

# Yahan apna Telegram Group ya Channel Chat ID daalein (jaise -100xxxxxxxxxx)
GROUP_CHAT_ID = os.environ.get("GROUP_CHAT_ID", "YOUR_GROUP_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)
USERS_FILE = "users.txt"
SEEN_LEADS_FILE = "seen_leads.txt"

def save_chat_id(chat_id):
    chat_id_str = str(chat_id)
    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
    if chat_id_str not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{chat_id_str}\n")

def is_already_sent(lead_id):
    if not os.path.exists(SEEN_LEADS_FILE):
        return False
    with open(SEEN_LEADS_FILE, "r") as f:
        seen = f.read().splitlines()
    return lead_id in seen

def mark_as_sent(lead_id):
    with open(SEEN_LEADS_FILE, "a") as f:
        f.write(f"{lead_id}\n")

# --- UPWORK, REDDIT & WEB LEAD SCRAPER ---
def run_lead_scraper():
    print("🚀 Upwork, Reddit & Web Lead Scraper Started...")
    while True:
        try:
            leads = []

            # 1. Reddit Freelance / Jobs Feeds (JSON)
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                r = requests.get("https://www.reddit.com/r/freelance_forhire/new.json?limit=5", headers=headers, timeout=10)
                if r.status_code == 200:
                    posts = r.json().get('data', {}).get('children', [])
                    for post in posts:
                        p_data = post['data']
                        lead_id = f"reddit_{p_data['id']}"
                        title = p_data['title']
                        url = f"https://reddit.com{p_data['permalink']}"
                        if not is_already_sent(lead_id):
                            leads.append((lead_id, f"🔥 **New Reddit Lead:**\n\n{title}\n\n🔗 {url}"))
            except Exception as e:
                print(f"Reddit Scraper Error: {e}")

            # 2. Upwork Public RSS Feed (Python/Freelance jobs)
            try:
                r = requests.get("https://www.upwork.com/ab/feed/jobs/rss?q=python&sort=recency", timeout=10)
                if r.status_code == 200 and "<item>" in r.text:
                    # Basic XML parsing for RSS items
                    items = r.text.split("<item>")
                    for item in items[1:4]: # Top 3 latest
                        if "<title>" in item and "<link>" in item:
                            title = item.split("<title>")[1].split("</title>")[0].replace("<![CDATA[", "").replace("]]>", "")
                            link = item.split("<link>")[1].split("</link>")[0].strip()
                            lead_id = f"upwork_{link.split('/')[-1]}"
                            if not is_already_sent(lead_id):
                                leads.append((lead_id, f"💼 **New Upwork Job:**\n\n{title}\n\n🔗 {link}"))
            except Exception as e:
                print(f"Upwork Scraper Error: {e}")

            # Send accumulated leads to Telegram Group
            if GROUP_CHAT_ID != "YOUR_GROUP_CHAT_ID":
                for lead_id, lead_msg in leads:
                    try:
                        bot.send_message(GROUP_CHAT_ID, lead_msg, parse_mode="Markdown")
                        mark_as_sent(lead_id)
                        time.sleep(3) # Anti-spam delay
                    except Exception as e:
                        print(f"Telegram Send Error: {e}")

            # Check for new leads every 15 minutes
            time.sleep(900)
        except Exception as e:
            print(f"Scraper General Error: {e}")
            time.sleep(60)

# --- TELEGRAM BOT HANDLERS ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    save_chat_id(message.chat.id)
    welcome_msg = (
        "🤖 **Welcome to Hermes AI Freelance Agent!**\n\n"
        "I scrape live jobs from Upwork, Reddit, and web sources automatically.\n"
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
        UPI_ID = "navinder000100@oksbi"
        AMOUNT = "299"
        QR_URL = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=HermesAI%26am={AMOUNT}%26cu=INR"
        bot.send_photo(message.chat.id, QR_URL, caption=f"⚡ Pay ₹{AMOUNT} to UPI `{UPI_ID}` and reply with UTR/Paid.", parse_Mode="Markdown")

def run_bot():
    print("🚀 Starting Telegram Bot Polling...")
    try:
        bot.delete_webhook()
    except Exception:
        pass
    bot.infinity_polling()

if __name__ == "__main__":
    # 1. Scraper Background Thread
    scraper_thread = threading.Thread(target=run_lead_scraper)
    scraper_thread.daemon = True
    scraper_thread.start()

    # 2. Telegram Bot Thread
    run_bot()
            
