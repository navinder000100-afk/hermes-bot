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

TELEGRAM_BOT_TOKEN = "8855388070:AAGX5TPJjB5p7jSfIdiz1GJv-VzAYHj7_6s"
TELEGRAM_CHAT_ID = "8104262282"
UPI_ID = "navinder000100@oksbi"
PACKAGE_PRICE = "999"  # 100% direct to your bank, 0% fee

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermas Revenue Machine v3.0 is Online 24/7!"

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def send_telegram_message(text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def run_revenue_funnel():
    log_event("Executing revenue funnel cycle...")
    simulated_target = f"@lead_user_{random.randint(1000, 9999)}"
    chosen_niche = "Python Automation & Telegram Monetization"
    
    pitch_text = (
        f"⚡ *Autonomous Business Pitch*\n\n"
        f"Target: {simulated_target}\n"
        f"Niche: {chosen_niche}\n\n"
        f"Unlock the full automation system today for just ₹{PACKAGE_PRICE}!\n"
        f"Pay directly via UPI: `{UPI_ID}`\n"
        f"Send screenshot here after payment."
    )
    
    send_telegram_message(pitch_text)
    
    # Log pending transaction
    file_exists = os.path.exists(LEAD_CSV)
    with open(LEAD_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Target", "Niche", "Status", "Amount"])
        writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), simulated_target, chosen_niche, "Pitch Sent - Pending Payment", "0"])
    
    log_event(f"Pitch deployed for {simulated_target}. Waiting for payment clearance.")

def run_flask_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_flask_server)
    server_thread.daemon = True
    server_thread.start()

    log_event("Revenue Machine v3.0 Online.")
    send_telegram_message("⚡ **Autonomous Revenue Machine v3.0** is active and hunting for paying clients!")

    while True:
        try:
            run_revenue_funnel()
        except Exception as e:
            log_event(f"Error: {e}")
        
        # Cycle delay before targeting next monetization (Runs every 4 hours)
        time.sleep(14400)
