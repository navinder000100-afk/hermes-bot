import os
import requests
from flask import Flask

TELEGRAM_BOT_TOKEN = "8855388070:AAGX5TPJjB5p7jSfIdiz1GJv-VzAYHj7_6s"
CHANNEL_ID = "-10044292540"
UPI_ID = "navinder000100@oksbi"
PACKAGE_PRICE = "999"

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermas Bot v3.7 Online! Channel par message bhejne ke liye browser mein /send open karein."

@app.route('/send')
def send_now():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID, 
        "text": f"⚡ **Hermas Agent v3.7 Active!**\n\nScale your traffic and automated funnels instantly for just ₹{PACKAGE_PRICE}!\n💳 Pay directly via UPI: `{UPI_ID}`\nSend screenshot of payment to activate system instantly."
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return f"Telegram API Response -> Status: {response.status_code} | Body: {response.text}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
