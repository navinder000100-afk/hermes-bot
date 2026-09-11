import os
import requests
from flask import Flask, request
from groq import Groq

# 1. FLASK APP INITIALIZATION
app = Flask(__name__)

# 2. ENVIRONMENT VARIABLES
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
VIP_CHANNEL_ID = os.environ.get('VIP_CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Initialize Groq Client
groq_client = Groq(api_key=GROQ_API_KEY)

# 3. HOME ROUTE FOR RENDER HEALTH CHECK
@app.route('/')
def home():
    return "🚀 5-in-1 Master AI Sales Ecosystem is Active and Live!"

# 4. TELEGRAM WEBHOOK FOR PERSONAL DM AI REPLIES
@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    
    # Check if update is a direct message containing text
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        # Prevent responding to channel posts via webhook
        if str(chat_id) == str(VIP_CHANNEL_ID):
            return "OK", 200

        # Generate AI Response via Groq AI
        try:
            completion = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are an expert sales AI assistant. Help clients directly with quick, professional, and clear answers."},
                    {"role": "user", "content": user_text}
                ]
            )
            ai_reply = completion.choices[0].message.content
        except Exception as e:
            print(f"Error in Groq Processing: {e}")
            ai_reply = "Hello! I received your message. How can I assist you with your project today?"

        # Send direct DM reply back to user
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": ai_reply
        }
        requests.post(url, json=payload)

    return "OK", 200

# 5. POST LEADS TO VIP CHANNEL FUNCTION
def post_to_vip_channel(title, desc, link):
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

# 6. MAIN SERVER LAUNCH
if __name__ == "__main__":
    print("🤖 Master Engine fully booted and ready...")
    # Bind properly to the dynamic PORT assigned by Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
