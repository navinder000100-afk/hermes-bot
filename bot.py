import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# Credentials
TELEGRAM_TOKEN = "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE"
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
VIP_CHANNEL_ID = "-1004429254980"

# Gemini AI Setup (Gemini 3.6 / Latest Preview Model)
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Gemini 3.6 model string
    model = genai.GenerativeModel('gemini-3-flash-preview')

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

        # Generate AI response using Gemini 3.6
        try:
            response = model.generate_content(
                f"You are Hermes AI Agent, an expert freelance generation assistant. Answer accurately and concisely: {user_text}"
            )
            ai_reply = response.text
        except Exception as e:
            print(f"❌ GEMINI ERROR: {e}", flush=True)
            ai_reply = f"⚠️ Gemini AI Error: {e}"

        # Send Telegram DM
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": ai_reply}

        try:
            resp = requests.post(url, json=payload)
            print(f"📤 TELEGRAM STATUS: {resp.status_code}", flush=True)
        except Exception as err:
            print(f"❌ SEND FAILED: {err}", flush=True)

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
