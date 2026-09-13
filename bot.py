import time
import datetime
import random
import csv
import os
import requests
from flask import Flask
import threading

LOG_FILE = "revenue_machine.log"
LEAD_CSV = "revenue_leads.csv"

TELEGRAM_BOT_TOKEN = "8855388070:AAGX5TPJjB5p7jSfIdiz1G"
TELEGRAM_CHAT_ID = "8104262282"
UPI_ID = "navinder000100@oksbi"
PACKAGE_PRICE = "999"  # 100% direct to your bank, 0% fee

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermas Revenue Machine v3.0 is Online 24/7!"

def send_telegram_message(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def run_flask_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# Apne baaki functions (jaise run_revenue_funnel, log_event, etc.) yahan beech mein rakh lena

if __name__ == "__main__":
    # Flask server ko alag thread mein start karein taaki Render sleep na ho
    server_thread = threading.Thread(target=run_flask_server)
    server_thread.daemon = True
    server_thread.start()

    print("Revenue Machine v3.0 Online.")
    send_telegram_message("⚡ **Autonomous Revenue Machine v3.0** is active and hunting for paying clients!")

    while True:
        try:
            # run_revenue_funnel()  # Apna main function yahan call karein
            pass
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(14400)  # Runs every 4 hours
        
