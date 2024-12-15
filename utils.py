# utils.py
import os
import requests
import logging
import re
from dotenv import load_dotenv
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def send_msg(message, subject="Notification"):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram bot token or chat ID is missing!")
        return

    sanitized_message = re.sub(r'[#&<>]', '', message)
    sanitized_subject = re.sub(r'[#&<>]', '', subject)
    full_message = f"{sanitized_subject}\n-----------\n{sanitized_message}"

    if len(full_message) > 4096:
        full_message = full_message[:4093] + "..."
    
    url_req = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={full_message}"
    try:
        results = requests.get(url_req)
        results.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send message: {e}")
