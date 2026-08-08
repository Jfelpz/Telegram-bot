"""
get_chat_id.py

Descobre automaticamente o CHAT_ID do Telegram.
"""

import requests
from src.config import TELEGRAM_BOT_TOKEN

URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"

response = requests.get(URL)

print(response.json())
