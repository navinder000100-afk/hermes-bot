import os
import sys
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# Fetch environment variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
VIP_CHANNEL_ID = os.environ.get('VIP_CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

@app.route('/')
def home():
    return "🚀 Hermes Sales Ecosystem Active!"

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    print(f"📥 RECEIVED DATA: {data}", flush=True)
    
    if data and "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"].get("text", "")
        
        # Skip VIP Channel messages
        if str(chat_id) == str(VIP_CHANNEL_ID):
            return "OK", 200

        if not user_text:
            print("⚠️ Message has no text content.", flush=True)
            return "OK", 200

        # Generate response using Groq AI
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
            print(f"❌ GROQ ERROR: {e}", flush=True)
            ai_reply = "Hello! Thanks for reaching out. How can I help you today?"

        # Send response back to Telegram
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": ai_reply}
        
        try:
            resp = requests.post(url, json=payload, timeout=10)
            print(f"📤 TELEGRAM STATUS: {resp.status_code} | RESPONSE: {resp.text}", flush=True)
        except Exception as err:
            print(f"❌ SEND FAILED: {err}", flush=True)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
