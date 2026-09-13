import time
import datetime
import random
import csv
import os
import requests
from bs4 import BeautifulSoup
from flask import Flask
import threading

LOG_FILE = "revenue_machine.log"
LEAD_CSV = "revenue_leads.csv"

TELEGRAM_BOT_TOKEN = "8855388070:AAGX5TPJjB5p7jSfIdiz1GJv-VzAYHj7_6s"

# Yahan apne sabhi target Groups AUR Channels ki chat IDs ki list daal do
# (Note: Channel mein post karne ke liye bot ko channel ka Admin banana zaroori hai)
TELEGRAM_TARGET_CHAT_IDS = [
    "8104262282",            # Aapka pehla group/channel
    # "-100xxxxxxxxxx",      # Aur bhi groups ya channels yahan add kar sakte hain
]

UPI_ID = "navinder000100@oksbi"
PACKAGE_PRICE = "999"

app = Flask(__name__)

@app.route('/')
def home():
    return "Hermas Multi-Target Broadcast Machine v3.1 Online 24/7!"

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_msg + "\n")

def send_telegram_broadcast_to_all(text):
    success_count = 0
    url_base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    for chat_id in TELEGRAM_TARGET_CHAT_IDS:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        try:
            response = requests.post(url_base, json=payload, timeout=10)
            if response.status_code == 200:
                success_count += 1
            else:
                log_event(f"Failed for target {chat_id}: {response.text}")
        except Exception as e:
            log_event(f"Telegram error for target {chat_id}: {e}")
        time.sleep(1) # Rate limit bachane ke liye gap
        
    return success_count

def scrape_real_leads_from_web():
    extracted_leads = []
    try:
        search_queries = [
            "site:t.me startup founders india",
            "site:t.me python developers channel",
            "site:t.me digital marketers group"
        ]
        
        for query in search_queries:
            url = f"https://html.duckduckgo.com/html/?q={query}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('a', class_='result__url'):
                    link = a.get('href', '')
                    if 't.me/' in link:
                        extracted_leads.append(link)
        
        return list(set(extracted_leads))
    except Exception as e:
        log_event(f"Scraping error: {e}")
        return []

def run_revenue_funnel():
    log_event("Scanning platforms and preparing multi-target broadcast...")
    live_leads = scrape_real_leads_from_web()
    
    target = random.choice(live_leads) if live_leads else "@target_business_lead"
    chosen_niche = "Cross-Platform Automation & Monetization"
    
    pitch_text = (
        f"🚀 *Business Automation & Lead Generation Pitch*\n\n"
        f"Target Verified Source: {target}\n"
        f"Category: {chosen_niche}\n\n"
        f"Scale your business traffic and automated funnels instantly for just ₹{PACKAGE_PRICE}!\n"
        f"💳 Pay directly via UPI: `{UPI_ID}`\n"
        f"Send screenshot of payment to activate system instantly."
    )
    
    success_count = send_telegram_broadcast_to_all(pitch_text)
    
    file_exists = os.path.exists(LEAD_CSV)
    with open(LEAD_CSV, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Target Source", "Targets Reached", "Status", "Amount"])
        writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), target, success_count, "Broadcast Sent", "0"])
    
    log_event(f"Broadcast completed. Successfully reached {success_count} targets (Groups/Channels).")

def run_flask_server():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_flask_server)
    server_thread.daemon = True
    server_thread.start()

    log_event("Hermas Multi-Target Broadcast Machine v3.1 Online.")
    send_telegram_broadcast_to_all("⚡ **Hermas Agent v3.1** Multi-Group & Channel target system is now active 24/7!")

    while True:
        try:
            run_revenue_funnel()
        except Exception as e:
            log_event(f"Error: {e}")
        
        # Har 2 ghante mein sabhi targets par naya broadcast chalega
        time.sleep(7200)
