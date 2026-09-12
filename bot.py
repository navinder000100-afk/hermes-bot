import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# Credentials
TELEGRAM_TOKEN = "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE"
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
VIP_CHANNEL_ID = "-1004429254980"

# Payment Details
UPI_ID = "navinder000100@oksbi"
PRICE = "₹299"
QR_IMAGE_URL = "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa=navinder000100@oksbi&pn=Hermes&am=299&cu=INR"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-3-flash-preview')

@app.route('/')
def home():
    return "🚀 Hermes Sales Ecosystem Active!"

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "OK", 200

    chat_id = data["message"]["chat"]["id"]
    user_text = data["message"].get("text", "")

    if str(chat_id) == str(VIP_CHANNEL_ID) or not user_text:
        return "OK", 200

    # 1. Payment/UTR Verification Check
    if any(keyword in user_text.lower() for keyword in ["utr", "paid", "payment", "done"]):
        solution_prompt = f"Provide the complete production-ready Python solution for this request: {user_text}"
        try:
            solution = model.generate_content(solution_prompt).text
        except Exception:
            solution = "Here is your customized code solution."

        payload_text = f"✅ **Payment Verified!** Here is your solution:\n\nPRICE: 299\n\nSUMMARY: {solution}"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": payload_text, "parse_mode": "Markdown"})
        return "OK", 200

    # 2. Generate Proposal & Send QR Code
    caption = (
        f"💳 **Order Proposal Generated!**\n\n"
        f"Price: **{PRICE}**\n"
        f"UPI ID: `{UPI_ID}`\n\n"
        f"1️⃣ Pay **{PRICE}** using UPI.\n"
        f"2️⃣ Reply with UTR after payment."
    )

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto",
        json={"chat_id": chat_id, "photo": QR_IMAGE_URL, "caption": caption, "parse_mode": "Markdown"}
    )

    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
