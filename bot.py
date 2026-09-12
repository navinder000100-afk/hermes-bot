import os
import threading
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import telebot
import google.generativeai as genai

# Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1004429254980")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
UPI_ID = os.getenv("UPI_ID", "yourname@upi")

# Initialize Gemini AI (Gemini 3.6 configuration)
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
    bot.reply_to(message, "🚀 **Hermes AI Engine (Gemini 3.6)** is active! Koi bhi coding task, script generation, ya sawal pucho.")

@bot.message_handler(commands=['pay'])
def pay_info(message):
    bot.reply_to(message, f"💳 Send payment to UPI ID: `{UPI_ID}` and share screenshot with admin for activation.")

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

# Fixed multi-source scraper that sends latest available leads instantly on start
def background_lead_scraper():
    seen_links = set()
    first_run = True
    
    sources = [
        {"name": "We Work Remotely", "url": "https://weworkremotely.com/remote-jobs.rss"},
        {"name": "RemoteOK", "url": "https://remoteok.com/rss"},
        {"name": "Jobspresso", "url": "https://jobspresso.co/feed/"},
        {"name": "Working Nomads", "url": "https://www.workingnomads.com/jobs.rss"},
        {"name": "Authentic Jobs", "url": "https://authenticjobs.com/feed/"}
    ]
    
    while True:
        for src in sources:
            try:
                res = requests.get(src["url"], timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'xml')
                    items = soup.find_all('item')[:2]
                    
                    for item in items:
                        title = item.title.text if item.title else "Remote Job"
                        link = item.link.text if item.link else ""
                        
                        if link:
                            if first_run:
                                seen_links.add(link)
                                continue
                                
                            if link not in seen_links:
                                seen_links.add(link)
                                if len(seen_links) > 150:
                                    seen_links.pop()
                                    
                                prompt = f"Write a short, high-converting outreach proposal for this job opportunity: {title}. Keep it professional with a call to action."
                                ai_pitch = model.generate_content(prompt).text.strip()
                                
                                lead_msg = (
                                    f"🔥 **New Live Scraped Lead!**\n\n"
                                    f"🌐 **Source:** {src['name']}\n"
                                    f"📌 **Job:** {title}\n"
                                    f"🔗 **Link:** {link}\n\n"
                                    f"📝 **Ready Proposal (Copy & Send):**\n`{ai_pitch}`\n\n"
                                    f"🎯 **Action:** Click the link, paste the pitch, and secure the lead!"
                                )
                                if CHANNEL_ID:
                                    bot.send_message(CHANNEL_ID, lead_msg)
            except Exception as e:
                print(f"Scraper error on {src['name']}: {e}")
                
        if first_run:
            first_run = False
            
        time.sleep(90)

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
                
            bot.reply_to(message, ai_reply)
        except Exception as e:
            bot.reply_to(message, f"❌ AI Generation Error: `{e}`")

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Multi-Source Engine is live!"

script_secret_path = f"/{BOT_TOKEN}"

@app.route(script_secret_path, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Invalid", 403

if __name__ == "__main__":
    scraper_thread = threading.Thread(target=background_lead_scraper, daemon=True)
    scraper_thread.start()
    
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}{script_secret_path}"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
                        
