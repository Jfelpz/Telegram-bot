import os
import json
import uuid
import time
import gspread
import requests
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from zoneinfo import ZoneInfo

# ==========================
# CONFIGURAÇÕES
# ==========================

SHEET_ID = os.getenv("SHEET_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# ==========================
# GOOGLE SHEETS CONEXÃO
# ==========================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(GOOGLE_CREDENTIALS)
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    creds_dict,
    scope
)

client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID).sheet1
config_sheet = client.open_by_key(SHEET_ID).worksheet("CONFIG")

# ==========================
# DADOS (CORREÇÃO DEFINITIVA)
# ==========================

raw_data = sheet.get_all_records()

# mantém linha real + dados juntos
rows = list(enumerate(raw_data, start=2))

# ==========================
# CONTROLE DE TEMPO
# ==========================

INTERVALO = 1800

config_raw = config_sheet.get_all_records()

config = {}
for row in config_raw:
    key = str(row.get("CONFIGURAÇÃO", "")).strip()
    value = None
    for k, v in row.items():
        if k.strip().upper() != "CONFIGURAÇÃO":
            value = v
    config[key] = value

ultimo_envio = float(config.get("ULTIMO_ENVIO", 0))

if time.time() - ultimo_envio < INTERVALO:
    print("⏳ Ainda não passou o intervalo.")
    exit()

# ==========================
# TELEGRAM
# ==========================

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    requests.post(url, data=payload)

# ==========================
# SCORE
# ==========================

def calcular_score(row):
    score = 0

    prioridade = str(row.get("PRIORIDADE", "")).strip().upper()
    desconto = str(row.get("DESCONTO", "")).replace("%", "").replace(",", ".").strip()
    categoria = str(row.get("CATEGORIA", "")).strip().upper()

    try:
        desconto = float(desconto)
    except:
        desconto = 0

    if prioridade == "ALTA":
        score += 20
    elif prioridade == "MEDIA":
        score += 10
    else:
        score += 5

    score += desconto

    if categoria in ["GPU", "PLACA DE VIDEO", "PROCESSADOR", "SSD"]:
        score += 10

    return score

# ==========================
# ORDENAÇÃO SEGURA
# ==========================

rows.sort(key=lambda x: calcular_score(x[1]), reverse=True)

# ==========================
# ENVIO
# ==========================

posts_enviados = 0
limite = 1

for row_number, row in rows:

    if posts_enviados >= limite:
        break

    status = str(row.get("STATUS", "")).strip().upper()
    if status == "ENVIADO":
        continue

    produto = row.get("PRODUTO")
    preco = row.get("PREÇO")
    link = row.get("LINK_AFILIADO")

    if not produto or not link:
        continue

    preco_antigo = str(row.get("PREÇO_ANTIGO", "")).strip()
    desconto = str(row.get("DESCONTO", "")).strip()
    loja = str(row.get("LOJA", "")).strip()
    categoria = str(row.get("CATEGORIA", "")).strip()
    prioridade = str(row.get("PRIORIDADE", "")).strip().upper()

    try:
        desconto_valor = float(desconto.replace("%", "").replace(",", "."))
    except:
        desconto_valor = 0

    if prioridade != "ALTA" and desconto_valor < 15:
        continue

    # ======================
    # ID (SEGURANÇA TOTAL)
    # ======================

    produto_id = str(row.get("ID", "")).strip()

    if not produto_id:
        produto_id = str(uuid.uuid4())[:8]

        # 🚨 proteção contra linha inválida
        if row_number > 1:
            sheet.update_cell(row_number, 1, produto_id)

    # ======================
    # MENSAGEM
    # ======================

    mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b> 🔥

⚡ <b>{produto}</b>

🏪 Loja: {loja}
📂 Categoria: {categoria}

💰 <b>Preço atual:</b> R$ {preco}
"""

    if preco_antigo:
        mensagem += f"\n💸 <b>De:</b> R$ {preco_antigo}"

    if desconto:
        mensagem += f"\n📉 <b>Desconto:</b> {desconto}"

    mensagem += f"""

━━━━━━━━━━━━━━━

⏳ <b>ATENÇÃO:</b> Oferta pode acabar a qualquer momento.

📦 <b>Estoque limitado.</b>

🚀 <b>Aproveite antes que o preço aumente!</b>

👉 <a href="{link}">🔥 COMPRAR AGORA 🔥</a>

#promoção #hardware #oferta
"""

    enviar_telegram(mensagem)

    # ======================
    # UPDATE CONFIG (SEGURO)
    # ======================

    config_sheet.update_cell(1, 2, str(time.time()))

    # ======================
    # MARCAR COMO ENVIADO (PROTEÇÃO B1)
    # ======================

    if row_number > 1:
        sheet.update_cell(row_number, 5, "ENVIADO")

    # ======================
    # DATA POSTAGEM
    # ======================

    data_postagem = datetime.now(
        ZoneInfo("America/Fortaleza")
    ).strftime("%d/%m/%Y %H:%M")

    if row_number > 1:
        sheet.update_cell(row_number, 12, data_postagem)

    posts_enviados += 1
