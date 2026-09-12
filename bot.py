import os
import threading
import time
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request
import telebot
import google.generativeai as genai

# Environment Variables Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1004429254980")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
UPI_ID = os.getenv("UPI_ID", "yourname@upi")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "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")

# Initialize Gemini AI (Gemini 3.6-flash)
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {"temperature": 0.7, "max_output_tokens": 2000}
model = genai.GenerativeModel(model_name="gemini-3.6-flash", generation_config=generation_config)

bot = telebot.TeleBot(BOT_TOKEN)
PAID_USERS = []

# In-Memory Active Client Deals & Payments Database
ACTIVE_CLIENT_CONVERSATIONS = {}

def is_paid(user_id):
    return user_id in PAID_USERS or user_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_paid(message.from_user.id):
        bot.reply_to(message, "🔒 Access Denied. Use /pay for subscription.")
        return
    bot.reply_to(message, "🚀 **Hermes Ultimate AI Employee** is fully online! Zero-touch mode active: Scraping, Emailing, Negotiating & Executing.")

@bot.message_handler(commands=['pay'])
def pay_info(message):
    bot.reply_to(message, f"💳 Send subscription to UPI ID: `{UPI_ID}` and share screenshot with admin.")

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

@bot.message_handler(commands=['confirmpay'])
def confirm_payment(message):
    if message.from_user.id == ADMIN_ID:
        try:
            target_user = message.text.split()[1]
            if target_user in ACTIVE_CLIENT_CONVERSATIONS:
                ACTIVE_CLIENT_CONVERSATIONS[target_user]["stage"] = "paid"
                deliverable = ACTIVE_CLIENT_CONVERSATIONS[target_user].get("deliverable", "Completed Code Deliverable")
                
                bot.send_message(target_user, f"✅ **Payment Confirmed!**\n\nHere is your final project execution:\n\n```python\n{deliverable}\n```\n\nThank you!")
                bot.reply_to(message, f"Payment confirmed & deliverable sent to `{target_user}`!", parse_mode="Markdown")
            else:
                bot.reply_to(message, "Client session not found.")
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")
    else:
        bot.reply_to(message, "Permission denied.")

def send_outbound_email(client_email, subject, proposal_text):
    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "personalizations": [{"to": [{"email": client_email}]}],
        "from": {"email": "agent@hermesai.com"},
        "subject": subject,
        "content": [{"type": "text/plain", "value": proposal_text}]
    }
    try:
        response = requests.post("https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers)
        return response.status_code == 202
    except Exception as e:
        print(f"SendGrid Error: {e}")
        return False

def autonomous_lead_and_execution_engine():
    seen_links = set()
    sources = [
        {"name": "We Work Remotely", "url": "https://weworkremotely.com/remote-jobs.rss"},
        {"name": "RemoteOK", "url": "https://remoteok.com/rss"}
    ]
    
    while True:
        for src in sources:
            try:
                res = requests.get(src["url"], timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if res.status_code == 200:
                    root = ET.fromstring(res.content)
                    items = root.findall(".//item")[:1]
                    
                    for item in items:
                        title = item.find('title').text if item.find('title') is not None else "Job"
                        link = item.find('link').text if item.find('link') is not None else ""
                        
                        if link and link not in seen_links:
                            seen_links.add(link)
                            if len(seen_links) > 100:
                                seen_links.pop()
                                
                            prompt = f"Write a high-converting cold outreach email proposal for this job: '{title}."
                            ai_pitch = model.generate_content(prompt).text.strip()
                            
                            send_outbound_email("client@targetdomain.com", f"Proposal for {title}", ai_pitch)
                            
                            lead_msg = (
                                f"🤖 **Autonomous Lead & Email Dispatched!**\n\n"
                                f"📌 **Job:** {title}\n"
                                f"🔗 **Link:** {link}\n"
                                f"✉️ **SendGrid Outbound Active**"
                            )
                            if CHANNEL_ID:
                                bot.send_message(CHANNEL_ID, lead_msg)
            except Exception as e:
                print(f"Engine Error: {e}")
        time.sleep(120)

@bot.message_handler(func=lambda message: True)
def handle_autonomous_negotiation_and_work(message):
    if not is_paid(message.from_user.id):
        bot.reply_to(message, "❌ Pehle subscription le bhai! (`/pay`)", parse_mode="Markdown")
        return
    
    user_msg = message.text.strip()
    user_id = str(message.from_user.id)
    
    if user_id not in ACTIVE_CLIENT_CONVERSATIONS:
        ACTIVE_CLIENT_CONVERSATIONS[user_id] = {
            "stage": "negotiating",
            "history": [],
            "deliverable": ""
        }
    
    client_session = ACTIVE_CLIENT_CONVERSATIONS[user_id]
    
    if client_session["stage"] == "paid":
        bot.reply_to(message, "Aapka project pehle hi successfully deliver ho chuka hai!")
        return
        
    client_session["history"].append({"role": "user", "parts": [user_msg]})
    
    try:
        system_instructions = (
            "You are Hermes, a fully autonomous AI employee. Talk to the client, negotiate terms, "
            "finalize requirements, and generate the complete code/deliverable in your reply. "
            "Instruct them to pay via UPI before admin unlocks the final secure release."
        )
        
        chat_context = [{"role": "model", "parts": [system_instructions]}] + client_session["history"]
        response = model.generate_content(chat_context)
        ai_reply = response.text.strip()
        
        client_session["history"].append({"role": "model", "parts": [ai_reply]})
        
        if "def " in ai_reply or "import " in ai_reply or "class " in ai_reply:
            client_session["deliverable"] = ai_reply
            ai_reply += f"\n\n💳 **Deliverable Ready!** Please complete payment to UPI ID: `{UPI_ID}`. Admin will verify via `/confirmpay {user_id}` and unlock your files."
            
        if len(ai_reply) > 4000:
            ai_reply = ai_reply[:4000] + "\n\n*(Truncated)*"
            
        bot.reply_to(message, ai_reply)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: `{e}`", parse_mode="Markdown")

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermes Ultimate AI Employee Engine is live!"

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
    engine_thread = threading.Thread(target=autonomous_lead_and_execution_engine, daemon=True)
    engine_thread.start()
    
    if RENDER_EXTERNAL_URL:
        webhook_url = f"{RENDER_EXTERNAL_URL}{script_secret_path}"
        bot.remove_webhook()
        bot.set_webhook(url=webhook_url)
        print(f"Webhook set to: {webhook_url}")
        
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
                        
