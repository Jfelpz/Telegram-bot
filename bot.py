import os
import json
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from zoneinfo import ZoneInfo

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

# 1. Primeiro conecta na planilha
sheet = client.open_by_key(SHEET_ID).sheet1

# 2. Depois pega os dados
data = sheet.get_all_records()

# 3. Ordenação por prioridade
prioridade_ordem = {
    "ALTA": 1,
    "MEDIA": 2,
    "BAIXA": 3
}

data.sort(
    key=lambda row: prioridade_ordem.get(
        str(row.get("PRIORIDADE", "BAIXA")).upper(),
        3
    )
)
def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, data=payload)

posts_enviados = 0
limite = 1    #Quantidade de posts por hora#

for i, row in enumerate(data, start=2):

    if posts_enviados >= limite:
        break

    if row.get("status") == "ENVIADO":
        continue

    produto = row.get("PRODUTO")
    preco = row.get("PREÇO")
    link = row.get("LINK_AFILIADO")
    preco_antigo = str(row.get("PREÇO_ANTIGO", "")).strip()
    desconto = str(row.get("DESCONTO", "")).strip()
    loja = str(row.get("LOJA", "")).strip()
    categoria = str(row.get("CATEGORIA", "")).strip()
    desconto_valor = str(row.get("DESCONTO", "")).replace("%", "").strip()
    prioridade = str(row.get("PRIORIDADE", "")).strip().upper()
    
    if desconto_valor:
        desconto_valor = float(desconto_valor)
    else:
        desconto_valor = 0
    
    # FILTRO DE QUALIDADE
    if prioridade != "ALTA" and desconto_valor < 15:
        continue

    mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b> 🔥

🖥️ <b>{produto}</b>

🏪 Loja: {loja}
📂 Categoria: {categoria}

💰 Preço: R$ {preco}
"""

if preco_antigo:
    mensagem += f"\n💸 <b>De:</b> R$ {preco_antigo}"

if desconto:
    mensagem += f"\n📉 <b>Desconto:</b> {desconto}%"

mensagem += f"""

━━━━━━━━━━━━━━━

⚠️ <b>ATENÇÃO:</b> preço pode mudar a qualquer momento ou acabar rápido.

⏳ <b>Estoque limitado</b> — disponível por tempo reduzido.

🚀 <b>Não perca essa oportunidade</b>

👉 <a href="{link}">COMPRAR AGORA</a>

#promoção #hardware #oferta
"""
    enviar_telegram(mensagem)

    sheet.update_cell(i, 5, "ENVIADO")

    data_postagem = datetime.now(
        ZoneInfo("America/Fortaleza")
    ).strftime("%d/%m/%Y %H:%M")

    sheet.update_cell(i, 12, data_postagem)

    posts_enviados += 1


