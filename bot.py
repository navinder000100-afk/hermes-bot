import time
import datetime
import random
import os
import requests
from flask import Flask
import threading

TELEGRAM_BOT_TOKEN = "8855388070:AAGX5TPJjB5p7jSfIdiz1GJv-VzAYHj7_6s"
CHANNEL_ID = "-10044292540"
UPI_ID = "navinder000100@oksbi"
PACKAGE_PRICE = "999"

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermas Direct Broadcast v3.5 Online 24/7!"

def send_test_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID, 
        "text": f"⚡ **Hermas Agent v3.5 Active!**\n\nScale your traffic and automated funnels instantly for just ₹{PACKAGE_PRICE}!\n💳 Pay directly via UPI: `{UPI_ID}`\nSend screenshot of payment to activate system instantly."
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"TELEGRAM API RESPONSE: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def run_flask_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_flask_server)
    server_thread.daemon = True
    server_thread.start()

    time.sleep(3)
    print("Sending startup broadcast to channel...")
    send_test_message()

    while True:
        try:
            send_test_message()
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(7200)
        
