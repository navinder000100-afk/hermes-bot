import os
import smtplib
import requests
import feedparser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask
from threading import Thread
from groq import Groq

# ---------------------------------------------------------
# 1. FLASK WEB SERVER FOR RENDER (24/7 BINDING)
# ---------------------------------------------------------
app = Flask('')

@app.route('/')
def home():
    return "🚀 5-in-1 Master AI Sales Ecosystem is Live and Running!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Run server in a background thread
Thread(target=run_flask).start()

# ---------------------------------------------------------
# 2. ENVIRONMENT VARIABLES
# ---------------------------------------------------------
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')  # Your Admin Chat ID
VIP_CHANNEL_ID = os.environ.get('VIP_CHANNEL_ID')      # Your VIP Channel ID (e.g. @your_channel or -100xxx)
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GMAIL_USER = os.environ.get('GMAIL_USER')
GMAIL_APP_PASS = os.environ.get('GMAIL_APP_PASS')
MY_UPI_ID = os.environ.get('MY_UPI_ID')
PAYONEER_LINK = os.environ.get('PAYONEER_LINK')
AFFILIATE_HOSTING_LINK = os.environ.get('AFFILIATE_HOSTING_LINK', 'https://www.hostinger.com/')

groq_client = Groq(api_key=GROQ_API_KEY)

# ---------------------------------------------------------
# 3. TELEGRAM BOT FUNCTIONS
# ---------------------------------------------------------
def post_to_vip_channel(title, desc, link):
    """Post high-ticket leads to VIP Telegram Channel"""
    if not VIP_CHANNEL_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    message = (
        f"🔥 **HIGH-TICKET LEAD ALERT**\n\n"
        f"📌 **Title:** {title}\n"
        f"📝 **Description:** {desc[:250]}...\n\n"
        f"🔗 [Apply / View Original Post]({link})"
    )
    payload = {
        'chat_id': VIP_CHANNEL_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error posting to VIP channel: {e}")

def send_telegram_approval_request(client_name, client_email, amount):
    """Send payment approval button to Admin Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    message = (
        f"💰 **NEW PAYMENT SCREENSHOT RECEIVED**\n\n"
        f"👤 **Client:** {client_name}\n"
        f"✉️ **Email:** {client_email}\n"
        f"💵 **Amount:** {amount}\n\n"
        f"Please verify in your GPay / PhonePe / Payoneer app and approve below:"
    )
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown',
        'reply_markup': {
            'inline_keyboard': [[
                {'text': '✅ Accept & Send Access', 'callback_data': f'accept_{client_email}'},
                {'text': '❌ Reject Payment', 'callback_data': f'reject_{client_email}'}
            ]]
        }
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending approval alert: {e}")

# ---------------------------------------------------------
# 4. GMAIL AUTO-PITCHER WITH DUAL PAYMENTS & AFFILIATE
# ---------------------------------------------------------
def send_email_pitch(client_email, project_title, pitch_text, is_international=False):
    """Send AI Pitch, Domestic UPI/Payoneer link, and Affiliate link"""
    if not GMAIL_USER or not GMAIL_APP_PASS:
        print("Gmail credentials not set. Skipping email.")
        return

    payment_info = f"Payoneer Direct Link: {PAYONEER_LINK}" if is_international else f"UPI ID: {MY_UPI_ID}"
    
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = client_email
    msg['Subject'] = f"Solution for your request: {project_title}"
    
    body = f"""Hi there,

{pitch_text}

---
💳 **Payment Details to Start Immediately:**
{payment_info}

🚀 **Recommended Tool / Hosting Resource for this Project:**
{AFFILIATE_HOSTING_LINK}

*Note: Reply directly to this email with your payment screenshot to trigger instant project setup & delivery.*

Best regards,
Automation & Media Agency
"""
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.send_message(msg)
        server.quit()
        print(f"✅ Pitch email successfully sent to {client_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ---------------------------------------------------------
# 5. GROQ AI ANALYSIS & PITCH GENERATION
# ---------------------------------------------------------
def analyze_and_pitch(lead_title, lead_desc, lead_link, client_email=None):
    """Filter quality leads with Groq AI and send pitches"""
    prompt = f"""
    Analyze this lead:
    Title: {lead_title}
    Description: {lead_desc}

    Task:
    1. Determine if this is a serious hiring/client post for development, video editing, or AI services.
    2. Write a short, highly persuasive 3-sentence proposal explaining how we can complete this project efficiently.
    """
    
    try:
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        ai_pitch = response.choices[0].message.content
        
        # 1. Post to VIP Channel
        post_to_vip_channel(lead_title, lead_desc, lead_link)
        
        # 2. Direct Pitch via Email if client email is extracted
        if client_email:
            send_email_pitch(client_email, lead_title, ai_pitch, is_international=True)
            
    except Exception as e:
        print(f"Error in Groq Processing: {e}")

# ---------------------------------------------------------
# 6. LEAD SCRAPER ENGINE (Upwork / RSS / Web)
# ---------------------------------------------------------
def fetch_jobs():
    """Scrape RSS Feeds for Freelance & Video Editing Jobs"""
    rss_urls = [
        "https://www.upwork.com/ab/feed/jobs/rss?q=python",
        "https://www.upwork.com/ab/feed/jobs/rss?q=video+editing"
    ]
    
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:  # Top 3 latest leads
            analyze_and_pitch(entry.title, entry.summary, entry.link)

# ---------------------------------------------------------
# 7. MAIN BOT LOOP
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🤖 Master Engine fully booted and ready...")
    # Fetch jobs once on startup
    try:
        fetch_jobs()
    except Exception as e:
        print(f"Initial run completed with note: {e}")
