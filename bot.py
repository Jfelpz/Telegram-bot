import os
import json
import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

# Configurações
SHEET_ID = os.getenv("SHEET_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# Conectar no Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(GOOGLE_CREDENTIALS)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID).sheet1
data = sheet.get_all_records()

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

for i, row in enumerate(data, start=2):

    if row.get("status") == "ENVIADO":
        continue

    produto = row.get("PRODUTO")
    preco = row.get("PREÇO")
    link = row.get("LINK_AFILIADO")

    mensagem = f"""
🔥 <b>OFERTA IMPERDÍVEL</b> 🔥

🖥️ {produto}

💰 <b>{preco}</b>

👉 <a href="{link}">Comprar agora</a>

#promoção #hardware #oferta
"""

    enviar_telegram(mensagem)

    sheet.update_cell(i, 5, "ENVIADO")
