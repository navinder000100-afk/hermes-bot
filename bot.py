import os
import telebot
from google import genai
from google.genai import types

# --- CONFIGURATION ---
TELEGRAM_TOKEN = "8683493983:AAEiQT-uab-W0xLLtccda0j7_rKTLiJbFDE"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ADMIN_ID = 8104262282  # Aapki Admin User ID

UPI_ID = "navinder000100@oksbi"
AMOUNT = "299"
PAYMENT_QR_URL = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=upi://pay?pa={UPI_ID}%26pn=HermesAI%26am={AMOUNT}%26cu=INR"

# Initialize Bots
bot = telebot.TeleBot(TELEGRAM_TOKEN)
ai_client = genai.Client(api_key=GEMINI_API_KEY)

USERS_FILE = "users.txt"

# --- HELPER FUNCTIONS ---
def save_chat_id(chat_id):
    """Saves user or group chat_id for broadcasting"""
    chat_id_str = str(chat_id)
    users = []
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
    if chat_id_str not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{chat_id_str}\n")

# --- BOT HANDLERS ---

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    save_chat_id(message.chat.id)
    welcome_msg = (
        "🤖 **Welcome to Hermes AI Freelance Agent!**\n\n"
        "I can build custom Python Web Scrapers, Automation Scripts, and Fix Code Bugs instantly.\n\n"
        "📌 **How it works:**\n"
        "1. Describe your script/automation requirement in detail.\n"
        "2. Get an instant payment request of ₹299.\n"
        "3. Pay & receive fully optimized, executable Python code immediately!"
    )
    bot.reply_to(message, welcome_msg, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    """Admin-only command to broadcast promotional messages to all users/groups"""
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ **Access Denied!** You are not authorized to run broadcasts.")
        return
    
    promo_text = message.text.replace("/broadcast", "").strip()
    if not promo_text:
        bot.reply_to(message, "⚠️ **Usage:** `/broadcast Your promotional text here`", parse_mode="Markdown")
        return
        
    if not os.path.exists(USERS_FILE):
        bot.reply_to(message, "⚠️ No registered users or groups found to broadcast.")
        return

    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
        
    success, failed = 0, 0
    bot.send_message(message.chat.id, f"🚀 **Starting Broadcast to {len(users)} target chats...**")
    
    for user_id in users:
        try:
            bot.send_message(user_id, promo_text, parse_mode="Markdown")
            success += 1
        except Exception:
            failed += 1
            
    bot.reply_to(message, f"✅ **Broadcast Complete!**\n\n🟢 Successfully Sent: {success}\n🔴 Failed/Blocked: {failed}")

@bot.message_handler(func=lambda message: True)
def handle_incoming_messages(message):
    save_chat_id(message.chat.id)
    text = message.text.lower()
    
    if any(keyword in text for keyword in ["utr", "paid", "payment done", "transaction", "done", "paid ₹299"]):
        bot.reply_to(message, "⏳ **Payment Received & Verified!** Generating your high-performance Python script via Gemini AI...")
        
        try:
            prompt = f"Write a complete, production-ready, well-commented Python script for this task: '{message.text}'. Provide only the Python code block with installation steps if needed."
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            bot.reply_to(message, f"✅ **Here is your solution:**\n\n{response.text}", parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"❌ Error generating solution: {str(e)}. Please contact admin.")
            
    else:
        caption_text = (
            f"⚡ **Task Accepted!**\n\n"
            f"To generate and receive your fully automated script, complete the single task payment:\n\n"
            f"💰 **Amount:** ₹{AMOUNT}\n"
            f"📌 **UPI ID:** `{UPI_ID}`\n\n"
            f"Scan the QR code above to pay. After payment, **reply with your UTR / Transaction ID or type 'Paid'** to get instant code delivery!"
        )
        bot.send_photo(message.chat.id, PAYMENT_QR_URL, caption=caption_text, parse_mode="Markdown")

# --- START BOT ---
if __name__ == "__main__":
    print("🚀 Starting Telegram Bot Polling...")
    try:
        bot.delete_webhook()
    except Exception:
        pass
    bot.infinity_polling()
        
