import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

Thread(target=run).start()

import requests, time, re, os, urllib.parse, threading

TELEGRAM_TOKEN = "8683493983:AAGNxjjSLa0gFb6adEP5bs5yT_RpqkhrIV0"
GEMINI_API_KEY = "AQ.Ab8RN6JIkKvzj-1hj_PG3X1FweNG__Q3L9DsYSjavkuVEi7OzA"
ADMIN_CHAT_ID = "8104262282"
UPI_ID = "navinder000100@oksbi"
MODEL_NAME = "gemini-3.6-flash"

SYSTEM_INSTRUCTION = "You are Hermes CodeAgent, an autonomous Senior Developer & Pricing Architect. Analyze user request and output strictly in this format:\nPRICE: <299 for simple script, 599 for scraper/API, 1199 for complex automation, 1999 for full app>\nSUMMARY: <brief summary>\nCODE:\n```python\n<code_here>\n```\nEXPLANATION: <walkthrough>"

pending_orders = {}
seen_leads = set()

def extract_price_and_code(text):
    price_match = re.search(r"PRICE:\s*(\d+)", text)
    price = price_match.group(1) if price_match else "299"
    code_match = re.findall(r"```(?:python|sh|bash)?\n(.*?)```", text, re.DOTALL)
    code = code_match[0] if code_match else None
    return price, code

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print("[Send Error]:", e)

def send_photo(chat_id, photo_url, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    try:
        requests.post(url, json={"chat_id": chat_id, "photo": photo_url, "caption": caption}, timeout=15)
    except Exception as e:
        print("[Photo Error]:", e)

def send_document(chat_id, filepath, caption=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"
    try:
        with open(filepath, 'rb') as f:
            requests.post(url, data={'chat_id': chat_id, 'caption': caption}, files={'document': f}, timeout=25)
    except Exception as e:
        print("[Document Error]:", e)

def get_ai_response(prompt, system_prompt=SYSTEM_INSTRUCTION, retries=2):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    for attempt in range(retries):
        try:
            res = requests.post(url, json=payload, timeout=60).json()
            if "candidates" in res and res["candidates"]:
                return res["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            time.sleep(2)
    return "API Error: Unable to process request."

def generate_pitch(job_title, job_desc):
    pitch_prompt = f"Write a 2-sentence proposal pitch for: Title: {job_title}\nDesc: {job_desc[:200]}"
    sys_prompt = "You are an expert Freelance Proposal Writer. Keep under 30 words."
    return get_ai_response(pitch_prompt, system_prompt=sys_prompt)

def lead_hunter_engine():
    subreddits = ["forhire", "pythonjobs", "freelance_forhire"]
    keywords = ["python", "scraper", "scraping", "bot", "automation", "script"]
    headers = {"User-Agent": "Mozilla/5.0"}
    print("🔍 [LEAD HUNTER ACTIVE: REDDIT + UPWORK...]")
    while True:
        try:
            for sub in subreddits:
                url = f"https://www.reddit.com/r/{sub}/new.json?limit=10"
                res = requests.get(url, headers=headers, timeout=15)
                if res.status_code == 200:
                    posts = res.json().get("data", {}).get("children", [])
                    for post in posts:
                        p_data = post.get("data", {})
                        p_id = p_data.get("id")
                        title = p_data.get("title", "")
                        selftext = p_data.get("selftext", "")
                        permalink = f"https://reddit.com{p_data.get('permalink')}"
                        full_content = (title + " " + selftext).lower()
                        if p_id not in seen_leads and any(kw in full_content for kw in keywords):
                            if "hiring" in title.lower() or "looking for" in title.lower() or "need" in title.lower():
                                seen_leads.add(p_id)
                                pitch = generate_pitch(title, selftext)
                                lead_msg = f"🎯 **NEW REDDIT LEAD!**\n\n📌 **r/{sub}**: {title}\n🔗 **Link**: {permalink}\n\n⚡ **AI Pitch:**\n`{pitch}`"
                                send_message(ADMIN_CHAT_ID, lead_msg)

            upwork_rss = "https://www.upwork.com/ab/feed/jobs/rss?q=python+automation&sort=recency"
            u_res = requests.get(upwork_rss, headers=headers, timeout=15)
            if u_res.status_code == 200:
                items = re.findall(r'<item>(.*?)</item>', u_res.text, re.DOTALL)
                for item in items[:5]:
                    title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
                    link_match = re.search(r'<link>(.*?)</link>', item)
                    desc_match = re.search(r'<description><!\[CDATA\[(.*?)\]\]></description>', item)
                    if title_match and link_match:
                        u_title = title_match.group(1)
                        u_link = link_match.group(1)
                        u_desc = desc_match.group(1) if desc_match else ""
                        u_id = u_link.split("_")[-1] if "_" in u_link else u_link
                        if u_id not in seen_leads:
                            seen_leads.add(u_id)
                            pitch = generate_pitch(u_title, u_desc)
                            lead_msg = f"🟢 **NEW UPWORK JOB!**\n\n📝 **Title**: {u_title}\n🔗 **Link**: {u_link}\n\n⚡ **AI Pitch:**\n`{pitch}`"
                            send_message(ADMIN_CHAT_ID, lead_msg)
            time.sleep(300)
        except Exception as e:
            print("[Hunter Exception]:", e)
            time.sleep(60)

threading.Thread(target=lead_hunter_engine, daemon=True).start()

def get_updates(offset):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=5"
    try:
        return requests.get(url, timeout=10).json().get("result", [])
    except:
        return []

requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook?drop_pending_updates=true")

print("=== HERMES AGENCY AUTONOMOUS ENGINE ONLINE ===")
offset = 0

while True:
    updates = get_updates(offset)
    for update in updates:
        offset = update["update_id"] + 1
        if "callback_query" in update:
            cb = update["callback_query"]
            cb_data = cb.get("data", "")
            if cb_data.startswith("approve_"):
                client_id = cb_data.split("_")[1]
                if client_id in pending_orders:
                    order = pending_orders.pop(client_id)
                    send_message(client_id, "✅ **Payment Verified!** Here is your solution:\n\n" + order["ai_reply"])
                    if order["code"]:
                        filename = "script_deliverable.py"
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(order["code"])
                        send_document(client_id, filename, caption="📦 Downloadable Python File (.py)")
                        if os.path.exists(filename):
                            os.remove(filename)
                    send_message(ADMIN_CHAT_ID, f"🎉 Approved Client `{client_id}`!")
            elif cb_data.startswith("reject_"):
                client_id = cb_data.split("_")[1]
                pending_orders.pop(client_id, None)
                send_message(client_id, "❌ Payment verification failed.")

        elif "message" in update and "text" in update["message"]:
            chat_id = str(update["message"]["chat"]["id"])
            user_text = update["message"]["text"]
            print(f"\n📩 [NEW TASK]: {user_text}")
            send_message(chat_id, "⏳ **Analyzing Task & Calculating Price...**")
            ai_reply = get_ai_response(user_text)
            price_inr, code_content = extract_price_and_code(ai_reply)
            pending_orders[chat_id] = {"ai_reply": ai_reply, "code": code_content, "task": user_text, "price": price_inr}
            upi_link = f"upi://pay?pa={UPI_ID}&pn=HermesAgency&am={price_inr}&cu=INR"
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(upi_link)}"
            pay_msg = f"💳 **Order Proposal Generated!**\n\nPrice: **₹{price_inr}**\nUPI ID: `{UPI_ID}`\n\n1️⃣ Pay **₹{price_inr}** using UPI.\n2️⃣ Reply with UTR after payment."
            send_photo(chat_id, qr_url, caption=pay_msg)
            admin_markup = {
                "inline_keyboard": [[
                    {"text": f"✅ Approve (₹{price_inr})", "callback_data": f"approve_{chat_id}"},
                    {"text": "❌ Reject", "callback_data": f"reject_{chat_id}"}
                ]]
            }
            send_message(ADMIN_CHAT_ID, f"🚨 **NEW ORDER!**\nClient: `{chat_id}`\nTask: {user_text}\nPrice: ₹{price_inr}", reply_markup=admin_markup)
    time.sleep(1)

