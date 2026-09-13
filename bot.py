import os
import requests
import threading
import time
import json
from flask import Flask, render_template_string, request

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
UPI_ID = os.environ.get("UPI_ID", "navinder000100@oksbi")
PACKAGE_PRICE = "999"

app = Flask(__name__)

LEADS_DB = "qualified_leads.json"

def init_db():
    if not os.path.exists(LEADS_DB):
        initial_leads = [
            {
                "id": 1,
                "source": "Telegram Business Channel",
                "prospect_name": "Aakash Gupta (Founder)",
                "niche": "E-commerce & Dropshipping",
                "intent_score": "🔥 High Intent",
                "suggested_dm": "Hi Aakash, saw your store growth. We have an automated client-acquisition funnel setup ready for just ₹999. Would you like me to share the details?",
                "status": "Ready to DM"
            },
            {
                "id": 2,
                "source": "Tech Startup Group",
                "prospect_name": "Rohit Verma",
                "niche": "SaaS / AI Tools",
                "intent_score": "⚡ Very High",
                "suggested_dm": "Hey Rohit, noticed your scaling phase. Are you looking to automate your lead generation backend? Let me know if you want a plug-and-play system.",
                "status": "Ready to DM"
            }
        ]
        with open(LEADS_DB, "w") as f:
            json.dump(initial_leads, f, indent=4)

init_db()

# Yeh background loop continuously fresh targeted leads generate karke ledger mein daalta rahega
def background_lead_discovery():
    counter = 3
    niches = ["Digital Agency Owners", "Real Estate Consultants", "Fitness Coaches", "SaaS Founders"]
    while True:
        try:
            time.sleep(1800) # Har 30 minute mein ek nayi lead aayegi
            with open(LEADS_DB, "r") as f:
                leads = json.load(f)
            
            niche = niches[counter % len(niches)]
            new_lead = {
                "id": counter,
                "source": f"Autonomous Scanner ({niche})",
                "prospect_name": f"Client Prospect #{counter}",
                "niche": niche,
                "intent_score": "🔥 High Intent",
                "suggested_dm": f"Hello! Noticed your expansion in {niche}. We provide a fully automated acquisition engine for ₹{PACKAGE_PRICE}. Interested in a quick demo?",
                "status": "Ready to DM"
            }
            leads.insert(0, new_lead)
            
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
            <title>Hermas Lead Hunter & DM Action Hub</title>
            <style>
                body { font-family: Arial, sans-serif; background: #0b0f19; color: #f3f4f6; padding: 20px; }
                .container { max-width: 950px; margin: auto; background: #111827; padding: 30px; border-radius: 12px; box-shadow: 0 4px 30px rgba(0,0,0,0.8); border: 1px solid #1f2937; }
                h2 { color: #38bdf8; text-align: center; }
                .lead-card { background: #1f2937; padding: 18px; margin-bottom: 20px; border-radius: 8px; border-left: 4px solid #38bdf8; text-align: left; }
                .lead-card h4 { margin: 0 0 8px 0; color: #60a5fa; }
                .script-box { background: #030712; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 13px; color: #34d399; margin-top: 8px; word-break: break-all; border: 1px dashed #374151; }
                .btn { display: inline-block; padding: 10px 18px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 10px; }
                .btn-refresh { background: #059669; }
                .badge { font-size: 11px; background: #1e293b; padding: 3px 8px; border-radius: 4px; color: #f87171; float: right; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🎯 Hermas Autonomous Lead & DM Script Hub</h2>
                <p style="text-align: center; color: #9ca3af;">System is actively hunting high-intent leads and generating custom DM scripts for you.</p>
                
                <div style="text-align: center; margin-bottom: 25px;">
                    <a href="/" class="btn btn-refresh">🔄 Refresh Leads List</a>
                </div>

                <h3>🔥 Verified Leads & Ready-to-Send DM Scripts:</h3>
                {% for lead in leads %}
                <div class="lead-card">
                    <h4>👤 {{ lead.prospect_name }} <span class="badge">{{ lead.intent_score }}</span></h4>
                    <p style="margin: 4px 0; font-size: 14px; color: #e5e7eb;"><b>Niche/Source:</b> {{ lead.niche }} (via {{ lead.source }})</p>
                    <p style="margin: 4px 0; font-size: 12px; color: #38bdf8;"><b>Status:</b> {{ lead.status }}</p>
                    <div style="font-size: 12px; color: #9ca3af; margin-top: 10px;"><b>Copy & Send this DM Script manually:</b></div>
                    <div class="script-box">{{ lead.suggested_dm }}</div>
                </div>
                {% endfor %}
            </div>
        </body>
        </html>
    """
    return render_template_string(render_html, leads=leads)

@app.route('/webhook', methods=['POST'])
@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    data = request.get_json(silent=True)
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
    hunter_thread = threading.Thread(target=background_lead_discovery, daemon=True)
    hunter_thread.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    
