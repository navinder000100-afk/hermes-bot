import os
import requests
from flask import Flask, render_template_string, request

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8683493983:AAFJ0070H0bc6wYKVjeiiPhs2i01WAhYaIY")

# Yahan apne saare Target Groups aur Channels ki IDs dal di hain jahan message/lead share hoga
TELEGRAM_TARGET_CHAT_IDS = [
    "-10044292540",
    # Agar aur groups/channels hain toh unki ID yahan comma lagakar add kar le
]

UPI_ID = os.environ.get("UPI_ID", "navinder000100@oksbi")
PACKAGE_PRICE = "999"

app = Flask(__name__)

DEFAULT_MESSAGE = f"⚡ *Hermas Enterprise Agent Active!*\n\nScale your traffic and automated funnels instantly for just ₹{PACKAGE_PRICE}!\n💳 Pay directly via UPI: `{UPI_ID}`\nSend screenshot of payment to activate system instantly."

@app.route('/')
def home():
    render_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Hermas Ultimate Control Panel</title></head>
        <body style="font-family: Arial; padding: 20px; text-align: center; background: #0f172a; color: #f8fafc;">
            <div style="max-width: 600px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);">
                <h2 style="color: #38bdf8;">🚀 Hermas Automation Control Panel</h2>
                <p style="color: #94a3b8;">Status: <span style="color: #4ade80; font-weight: bold;">Online & Fully Operational</span></p>
                
                <textarea id="msg" rows="6" style="width: 100%; padding: 12px; font-size: 14px; background: #0f172a; color: #f8fafc; border: 1px solid #475569; border-radius: 8px;">{{ text }}</textarea><br><br>
                
                <button onclick="copyText()" style="padding: 12px 24px; font-size: 16px; background: #0ea5e9; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">📋 Copy Sales Copy</button>
                <br><br>
                <a href="/send" style="display: block; font-size: 16px; color: #fff; background: #22c55e; padding: 14px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-bottom: 10px;">🚀 Broadcast to All Groups/Channels</a>
                <a href="/set-webhook" style="display: block; font-size: 14px; color: #38bdf8; background: #334155; padding: 10px; text-decoration: none; border-radius: 8px;">🔗 Auto-Register Telegram Webhook</a>
            </div>
            <script>
                function copyText() {
                    var copyText = document.getElementById("msg");
                    copyText.select();
                    document.execCommand("copy");
                    alert("Sales copy copied successfully!");
                }
            </script>
        </body>
        </html>
    """
    return render_template_string(render_html, text=DEFAULT_MESSAGE)

@app.route('/send')
def send_now():
    url_base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    results = []
    for chat_id in TELEGRAM_TARGET_CHAT_IDS:
        payload = {"chat_id": chat_id, "text": DEFAULT_MESSAGE, "parse_mode": "Markdown"}
        try:
            response = requests.post(url_base, json=payload, timeout=10)
            results.append(f"Target {chat_id} -> Status: {response.status_code}")
        except Exception as e:
            results.append(f"Target {chat_id} -> Error: {e}")
    return "<br>".join(results)

@app.route('/set-webhook')
def set_webhook():
    render_url = request.host_url.rstrip('/')
    webhook_url = f"{render_url}/webhook"
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}"
    try:
        resp = requests.get(tg_url, timeout=10)
        return f"Webhook Registration Response: {resp.text} <br><br> Target Webhook: {webhook_url}"
    except Exception as e:
        return f"Webhook setup failed: {e}"

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").lower()
        
        if "/start" in text:
            reply_text = f"👋 *Welcome to Hermas Automation!*\n\nTo unlock the complete system, pay ₹{PACKAGE_PRICE} via UPI: `{UPI_ID}` and drop the screenshot here."
        elif "screenshot" in text or "paid" in text or "payment" in text:
            reply_text = "✅ *Payment Intent Received!*\n\nOur admin panel is verifying your transaction details. Access credentials will be dispatched shortly."
        else:
            reply_text = f"🤖 *Hermas Support Bot*\n\nSend ₹{PACKAGE_PRICE} to UPI ID: `{UPI_ID}` and share your payment screenshot to activate full access."
            
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": reply_text, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
        
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
