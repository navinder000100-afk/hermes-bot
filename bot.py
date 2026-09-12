import os
import threading
import time
import requests
import xml.etree.ElementTree as ET
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

# In-Memory Active Client Conversations (State Machine)
# Format: { user_id_or_client_key: {"history": [...], "status": "negotiating"} }
ACTIVE_CLIENT_CONVERSATIONS = {}

def is_paid(user_id):
    return user_id in PAID_USERS or user_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_paid(message.from_user.id):
        bot.reply_to(message, "🔒 Access Denied. Use /pay for subscription.")
        return
    bot.reply_to(message, "🤖 **Hermes Autonomous AI Employee** is live! Zero-touch mode activated. Main khud leads pakad raha hoon aur handle karunga.")

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

@bot.message_handler(commands=['status'])
def system_status(message):
    if not is_paid(message.from_user.id):
        return
    active_chats = len(ACTIVE_CLIENT_CONVERSATIONS)
    bot.reply_to(message, f"📊 **Autonomous Engine Status:**\n• Active Negotiations: `{active_chats}`\n• Mode: Zero-Touch Autonomous Execution", parse_mode="Markdown")

# Module 1 & 2 Combined: Autonomous Background Scraper & Negotiation Handler
def autonomous_execution_engine():
    seen_links = set()
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
                    root = ET.fromstring(res.content)
                    items = root.findall(".//item")[:2]
                    
                    for item in items:
                        title_el = item.find('title')
                        link_el = item.find('link')
                        
                        title = title_el.text if title_el is not None and title_el.text else "Remote Job"
                        link = link_el.text if link_el is not None and link_el.text else ""
                        
                        if link and link not in seen_links:
                            seen_links.add(link)
                            if len(seen_links) > 150:
                                seen_links.pop()
                                
                            # Step 1: Generate Autonomous Outreach Strategy
                            prompt = (
                                f"You are an autonomous AI business development agent. "
                                f"Analyze this job posting: '{title}'. Generate a persuasive, "
                                f"ready-to-send proposal that acts as the initial automated outreach."
                            )
                            ai_pitch = model.generate_content(prompt).text.strip()
                            
                            # Initialize autonomous tracking state for this lead
                            lead_key = f"lead_{abs(hash(link))}"
                            ACTIVE_CLIENT_CONVERSATIONS[lead_key] = {
                                "job_title": title,
                                "source": src['name'],
                                "link": link,
                                "history": [{"role": "model", "parts": [ai_pitch]}]
                            }
                            
                            # Broadcast to Channel with autonomous status
                            lead_msg = (
                                f"🤖 **Autonomous Lead Captured & Pitched!**\n\n"
                                f"🌐 **Source:** {src['name']}\n"
                                f"📌 **Job:** {title}\n"
                                f"🔗 **Link:** {link}\n\n"
                                f"📝 **AI Autonomous Outreach Sent:**\n`{ai_pitch}`\n\n"
                                f"⚡ *System is standing by for automatic client replies.*"
                            )
                            if CHANNEL_ID:
                                bot.send_message(CHANNEL_ID, lead_msg)
            except Exception as e:
                print(f"Autonomous Scraper Error on {src['name']}: {e}")
                
        time.sleep(90)

# Autonomous Chat & Negotiation Agent for incoming client replies
@bot.message_handler(func=lambda message: True)
def handle_autonomous_chat(message):
    if not is_paid(message.from_user.id):
        bot.reply_to(message, "❌ Pehle subscription le bhai! (`/pay`)", parse_mode="Markdown")
        return
    
    user_msg = message.text.strip()
    user_id = str(message.from_user.id)
    
    # Maintain user-specific or active negotiation thread state
    if user_id not in ACTIVE_CLIENT_CONVERSATIONS:
        ACTIVE_CLIENT_CONVERSATIONS[user_id] = {
            "history": []
        }
    
    chat_session = ACTIVE_CLIENT_CONVERSATIONS[user_id]
    chat_session["history"].append({"role": "user", "parts": [user_msg]})
    
    try:
        # Construct chat context with system instructions for automated negotiation & closing
        chat_context = [
            {
                "role": "model",
                "parts": ["You are Hermes, an autonomous AI employee that handles negotiations, talks to clients professionally, finalizes requirements, writes code or deliverables, and closes sales without human intervention."]
            }
        ] + chat_session["history"]
        
        response = model.generate_content(chat_context)
        ai_reply = response.text.strip()
        
        chat_session["history"].append({"role": "model", "parts": [ai_reply]})
        
        if len(ai_reply) > 4000:
            ai_reply = ai_reply[:4000] + "\n\n*(Truncated due to length)*"
            
        bot.reply_to(message, ai_reply)
    except Exception as e:
        bot.reply_to(message, f"❌ Autonomous Negotiation Error: `{e}`", parse_mode="Markdown")

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Fully Autonomous AI Employee Engine is live!"

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
    # Start the Background Autonomous Lead Scraper & Pitch Engine
    engine_thread = threading.Thread(target=autonomous_execution_engine, daemon=True)
    engine_thread.start()
    
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}{script_secret_path}"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
