import os
import requests
from flask import Flask, render_template_string

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8683493983:AAFJ0070H0bc6wYKVjeiiPhs2i01WAhYaIY")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-10044292540")
UPI_ID = os.environ.get("UPI_ID", "navinder000100@oksbi")
PACKAGE_PRICE = "999"

app = Flask(__name__)

MESSAGE_TEXT = f"⚡ *Hermas Agent Active!*\n\nScale your traffic and automated funnels instantly for just ₹{PACKAGE_PRICE}!\n💳 Pay directly via UPI: `{UPI_ID}`\nSend screenshot of payment to activate system instantly."

@app.route('/')
def home():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>Hermas Bot Panel</title></head>
        <body style="font-family: Arial; padding: 20px; text-align: center; background: #f4f4f9;">
            <h2>Hermas Bot Control Panel</h2>
            <textarea id="msg" rows="6" style="width: 100%; max-width: 500px; padding: 10px; font-size: 14px;">{{ text }}</textarea><br><br>
            <button onclick="copyText()" style="padding: 12px 24px; font-size: 16px; background: #0088cc; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">📋 Click karke Copy Karein</button>
            <br><br><br>
            <a href="/send" style="font-size: 16px; color: #fff; background: #28a745; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">🚀 Direct Channel Par Bheje</a>
            <script>
                function copyText() {
                    var copyText = document.getElementById("msg");
                    copyText.select();
                    document.execCommand("copy");
                    alert("Text Successfully Clipboard mein Copy ho gaya!");
                }
            </script>
        </body>
        </html>
    """, text=MESSAGE_TEXT)

@app.route('/send')
def send_now():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHANNEL_ID, "text": MESSAGE_TEXT, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        return f"Telegram API Response -> Status: {response.status_code} | Body: {response.text}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
                                 
