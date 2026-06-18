import os
import json
import gspread
import requests
from datetime import datetime
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
    preco_antigo = str(row.get("PREÇO_ANTIGO", "")).strip()
    desconto = str(row.get("DESCONTO", "")).strip()
    loja = str(row.get("LOJA", "")).strip()
    categoria = str(row.get("CATEGORIA", "")).strip()


mensagem = f"""

🔥 OFERTA IMPERDÍVEL 🔥

🖥️ {produto}

🏪 Loja: {loja}
📂 Categoria: {categoria}

💰 Preço: R$ {preco}
"""


if preco_antigo:
    mensagem += f"\n💸 Preço anterior: R$ {preco_antigo}"

if desconto:
    mensagem += f"\n📉 Desconto: {desconto}%"

mensagem += f"""


━━━━━━━━━━━━━━━

⚠️ Oferta sujeita a alteração de preço e estoque.

👉 <a href="{link}">COMPRAR AGORA</a>

#promocao #hardware #oferta
"""


enviar_telegram(mensagem)

sheet.update_cell(i, 5, "ENVIADO")

data_postagem = datetime.now().strftime("%d/%m/%Y %H:%M")
sheet.update_cell(i, 12, data_postagem)


