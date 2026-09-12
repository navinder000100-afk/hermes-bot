import os
import threading
import time
import requests
import xml.etree.ElementTree as ET
from flask import Flask, request
import telebot
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# Environment Variables Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1004429254980")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
UPI_ID = os.getenv("UPI_ID", "yourname@upi")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "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")

# Initialize Gemini AI (Gemini 3.6-flash)
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {"temperature": 0.7, "max_output_tokens": 2000}
model = genai.GenerativeModel(model_name="gemini-3.6-flash", generation_config=generation_config)

bot = telebot.TeleBot(BOT_TOKEN)
PAID_USERS = []

# In-Memory Active Client Deals & Payments Database
ACTIVE_CLIENT_CONVERSATIONS = {}

def safe_generate_content(model_instance, contents):
    """Automatically handles Gemini API 429 Rate Limits with exponential backoff retry."""
    max_retries = 4
    delay = 5
    for attempt in range(max_retries):
        try:
            return model_instance.generate_content(contents)
        except Exception as e:
            if "429" in str(e) or isinstance(e, ResourceExhausted):
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2
                    continue
            raise e

def is_paid(user_id):
    return user_id in PAID_USERS or user_id == ADMIN_ID

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_paid(message.from_user.id):
        bot.reply_to(message, "🔒 Access Denied. Use /pay for subscription.")
        return
    bot.reply_to(message, "🚀 **Hermes Ultimate AI Employee** is fully online! Zero-touch mode active with Rate-Limit Safe Engine.")

@bot.message_handler(commands=['pay'])
def pay_info(message):
    bot.reply_to(message, f"💳 Send subscription to UPI ID: `{UPI_ID}` and share screenshot with admin.")

@bot.message_handler(commands=['addpaid'])
def add_paid(message):
    if message.from_user.id == ADMIN_ID:
        try:
            uid = int(message.text.split()[1])
            if uid not in PAID_USERS:
                PAID_USERS.append(uid)
            bot.reply_to(message, f"Success! User `{uid}` ko access mil gaya hai.", parse_mode="Markdown")
        except:
            bot.reply_to(message, "Sahi format: `/addpaid <user_id>`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "Permission denied.")

@bot.message_handler(commands=['confirmpay'])
def confirm_payment(message):
    if message.from_user.id == ADMIN_ID:
        try:
            target_user = message.text.split()[1]
            if target_user in ACTIVE_CLIENT_CONVERSATIONS:
                ACTIVE_CLIENT_CONVERSATIONS[target_user]["stage"] = "paid"
                deliverable = ACTIVE_CLIENT_CONVERSATIONS[target_user].get("deliverable", "Completed Code Deliverable")
                
                bot.send_message(target_user, f"✅ **Payment Confirmed!**\n\nHere is your final project execution:\n\n```python\n{deliverable}\n
                
