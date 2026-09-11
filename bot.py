import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# Credentials hardcoded safely to prevent Render Env 404 URL bugs
TELEGRAM_TOKEN = "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE"
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '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')
VIP_CHANNEL_ID = "-1004429254980"

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
        
        # Ignore VIP Channel posts
        if str(chat_id) == str(VIP_CHANNEL_ID):
            return "OK", 200

        if not user_text:
            return "OK", 200

        # Generate AI response using active Groq Llama 3.1 model
        try:
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are an expert sales AI assistant. Help clients directly with quick, professional, and clear answers."},
                    {"role": "user", "content": user_text}
                ]
            )
            ai_reply = completion.choices[0].message.content
        except Exception as e:
            print(f"❌ GROQ ERROR: {e}", flush=True)
            ai_reply = "Hello! Thanks for reaching out. How can I assist you today?"

        # Send Telegram DM
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN.strip()}/sendMessage"
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
    
