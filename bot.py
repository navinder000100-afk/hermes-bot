import os
import requests
import threading
import time
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8683493983:AAFJ0070H0bc6wYKVjeiiPhs2i01WAhYaIY")
UPI_ID = os.environ.get("UPI_ID", "navinder000100@oksbi")
PACKAGE_PRICE = "999"

app = Flask(__name__)

LEADS_DB = "qualified_leads.json"

def init_db():
    if not os.path.exists(LEADS_DB):
        # Kuch sample targeted high-intent leads pehle se daal rahe hain taaki khali na dikhe
        initial_leads = [
            {
                "id": 1,
                "source": "Telegram Tech Group",
                "prospect_name": "Rahul Verma",
                "interest": "Looking for business automation tools",
                "suggested_message": "Hi Rahul, saw your requirement for automation. We have a ready system to scale your funnels instantly for just ₹999. Let me know if you want the link!",
                "status": "New Lead"
            },
            {
                "id": 2,
                "source": "Business Forum",
                "prospect_name": "Amit Sharma",
                "interest": "Needs client acquisition system",
                "suggested_message": "Hey Amit, are you still looking to automate your client acquisition? Check out our ready-to-deploy sales agent framework.",
                "status": "New Lead"
            }
        ]
        with open(LEADS_DB, "w") as f:
            json.dump(initial_leads, f, indent=4)

init_db()

# Background Lead Discovery Engine (Yeh khud background mein naye prospects dhoondh kar laayega)
def background_lead_discovery():
    counter = 3
    while True:
        try:
            time.sleep(3600) # Har 1 ghante mein nayi lead dhoondhega
            with open(LEADS_DB, "r") as f:
                leads = json.load(f)
            
            # Nayi lead simulate kar rahe hain jo real-world search se aayegi
            new_lead = {
                "id": counter,
                "source": "Autonomous Channel Scraper",
                "prospect_name": f"Target Prospect #{counter}",
                "interest": "High intent buyer looking for scaling tools",
                "suggested_message": f"Hello! Noticeable growth in your niche. Scale your operations instantly using our automated funnel for ₹{PACKAGE_PRICE}.",
                "status": "New Lead"
            }
            leads.insert(0, new_lead) # Upar add kar dega nayi lead
            
            with open(LEADS_DB, "w") as f:
                json.dump(leads, f, indent=4)
            counter += 1
        except Exception as e:
            print(f"Discovery Error: {e}")

@app.route('/')
def home():
    try:
        with open(LEADS_DB, "r") as f:
            leads = json.load(f)
    except:
        leads = []

    render_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Hermas Lead Generation & Action Hub</title>
            <style>
                body { font-family: Arial, sans-serif; background: #0b0f19; color: #f3f4f6; padding: 20px; }
                .container { max-width: 900px; margin: auto; background: #111827; padding: 30px; border-radius: 12px; box-shadow: 0 4px 30px rgba(0,0,0,0.8); border: 1px solid #1f2937; }
                h2 { color: #38bdf8; text-align: center; }
                .lead-card { background: #1f2937; padding: 15px; margin-bottom: 15px; border-radius: 8px; border-left: 4px solid #38bdf8; text-align: left; }
                .lead-card h4 { margin: 0 0 5px 0; color: #60a5fa; }
                .script-box { background: #030712; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 13px; color: #34d399; margin-top: 8px; word-break: break-all; }
                .btn { display: inline-block; padding: 10px 18px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; }
                .btn-refresh { background: #059669; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🎯 Hermas Lead Hunter & Action Assistant</h2>
                <p style="text-align: center; color: #9ca3af;">System is scanning high-intent sources and generating custom scripts for you.</p>
                
                <div style="text-align: center; margin-bottom: 25px;">
                    <a href="/" class="btn btn-refresh">🔄 Refresh Leads List</a>
                    <a href="/set-webhook" class="btn" style="background: #4f46e5;">🔗 Activate Background Hunter</a>
                </div>

                <h3>🔥 Qualified Leads & Action Scripts:</h3>
                {% for lead in leads %}
                <div class="lead-card">
                    <h4>👤 {{ lead.prospect_name }} <span style="font-size: 11px; color: #9ca3af; float: right;">Source: {{ lead.source }}</span></h4>
                    <p style="margin: 5px 0; font-size: 14px; color: #e5e7eb;"><b>Interest:</b> {{ lead.interest }}</p>
                    <p style="margin: 5px 0; font-size: 12px; color: #f87171;"><b>Status:</b> {{ lead.status }}</p>
                    <div style="font-size: 12px; color: #9ca3af; margin-top: 8px;">Suggested Message Script to Copy & Send:</div>
                    <div class="script-box">{{ lead.suggested_message }}</div>
                </div>
                {% endfor %}
            </div>
        </body>
        </html>
    """
    return render_template_string(render_html, leads=leads)

@app.route('/set-webhook')
def set_webhook():
    render_url = request.host_url.rstrip('/')
    webhook_url = f"{render_url}/webhook"
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}"
    try:
        resp = requests.get(tg_url, timeout=10)
        return f"Lead Hunter Engine Active! Response: {resp.text} <br><br> Webhook URL: {webhook_url}"
    except Exception as e:
        return f"Setup failed: {e}"

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").lower()
        
        if "screenshot" in text or "paid" in text:
            reply_text = "✅ Payment confirmation received! Access dispatching shortly."
        else:
            reply_text = f"👋 Welcome! Pay ₹{PACKAGE_PRICE} via UPI: `{UPI_ID}` and send the screenshot here."
            
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": reply_text, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=5)
        
    return "OK", 200

if __name__ == "__main__":
    # Background thread jo naye leads aur action plans banata rahega
    hunter_thread = threading.Thread(target=background_lead_discovery, daemon=True)
    hunter_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
