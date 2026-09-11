import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# Environment Variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
VIP_CHANNEL_ID = os.environ.get('VIP_CHANNEL_ID')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

# Groq Client Initialization
groq_client = Groq(api_key=GROQ_API_KEY)

@app.route('/')
def home():
    return "🚀 Hermes Sales Bot Active!"

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    
    if data and "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_text = data["message"]["text"]
        
        # Ignore VIP Channel Posts
        if str(chat_id) == str(VIP_CHANNEL_ID):
            return "OK", 200

        # Generate Reply using Groq AI
        try:
            completion = groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a professional AI sales assistant."},
                    {"role": "user", "content": user_text}
                ]
            )
            ai_reply = completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error: {e}")
            ai_reply = "Hello! I received your message."

        # Send Telegram DM
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": ai_reply})

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
