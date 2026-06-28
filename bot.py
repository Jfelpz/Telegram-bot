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
# CONFIG
# ==========================

SHEET_ID = os.getenv("SHEET_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# ==========================
# GOOGLE SHEETS
# ==========================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(GOOGLE_CREDENTIALS)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SHEET_ID)

# ⚠️ IMPORTANTE: nome EXATO da aba
sheet = spreadsheet.worksheet("MENU")
config_sheet = spreadsheet.worksheet("CONFIG")

# ==========================
# COLUNAS DA PLANILHA
# ==========================

header = sheet.row_values(1)
col = {name.strip(): idx + 1 for idx, name in enumerate(header)}

# ==========================
# CONFIG (ROBUSTA)
# ==========================

config_values = config_sheet.get_all_values()

config = {}

for row in config_values:
    if len(row) < 2:
        continue
    key = str(row[0]).strip().upper()
    value = row[1]
    config[key] = value

INTERVALO_MINUTOS = int(config.get("INTERVALO_MINUTOS", 30))
INTERVALO = INTERVALO_MINUTOS * 60

LIMITE_POSTS = int(config.get("LIMITE_POSTS", 1))
DESCONTO_MINIMO = float(config.get("DESCONTO_MINIMO", 15))
ULTIMO_ENVIO = float(config.get("ULTIMO_ENVIO", 0))
MODO_TESTE = str(config.get("MODO_TESTE", "FALSE")).upper() == "TRUE"

# ==========================
# CONTROLE DE TEMPO
# ==========================

agora = time.time()

if not MODO_TESTE and (agora - ULTIMO_ENVIO < INTERVALO):
    print("⏳ Intervalo ainda não atingido.")
    exit()

# ==========================
# DADOS
# ==========================

raw_data = sheet.get_all_records()
rows = list(enumerate(raw_data, start=2))

# ==========================
# TELEGRAM
# ==========================

def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    })

# ==========================
# SCORE
# ==========================

def calcular_score(row):
    score = 0

    prioridade = str(row.get("PRIORIDADE", "")).upper()
    desconto = str(row.get("DESCONTO", "")).replace("%", "").replace(",", ".")

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

    if str(row.get("CATEGORIA", "")).upper() in ["GPU", "PLACA DE VIDEO", "PROCESSADOR", "SSD"]:
        score += 10

    return score

# ==========================
# ORDENAR
# ==========================

rows.sort(key=lambda x: calcular_score(x[1]), reverse=True)

# ==========================
# FUNÇÃO SEGURA CONFIG UPDATE
# ==========================

def atualizar_ultimo_envio():
    values = config_sheet.get_all_values()

    for i, row in enumerate(values, start=1):
        if len(row) > 0 and str(row[0]).strip().upper() == "ULTIMO_ENVIO":
            config_sheet.update_cell(i, 2, str(time.time()))
            return

# ==========================
# ENVIO
# ==========================

posts_enviados = 0

for row_number, row in rows:

    if posts_enviados >= LIMITE_POSTS:
        break

    status = str(row.get("STATUS", "")).strip().upper()
    if status == "ENVIADO":
        continue

    produto = row.get("PRODUTO")
    preco = row.get("PREÇO")
    link = row.get("LINK_AFILIADO")

    if not produto or not link:
        continue

    desconto = str(row.get("DESCONTO", "")).strip()
    loja = str(row.get("LOJA", "")).strip()
    categoria = str(row.get("CATEGORIA", "")).strip()

    try:
        desconto_valor = float(desconto.replace("%", "").replace(",", "."))
    except:
        desconto_valor = 0

    if desconto_valor < DESCONTO_MINIMO:
        continue

    # ======================
    # ID
    # ======================

    if not row.get("ID"):
        produto_id = str(uuid.uuid4())[:8]
        sheet.update_cell(row_number, col["ID"], produto_id)

    # ======================
    # MENSAGEM
    # ======================

    mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b> 🔥

⚡ <b>{produto}</b>

🏪 Loja: {loja}
📂 Categoria: {categoria}

💰 <b>Preço:</b> R$ {preco}

👉 <a href="{link}">🔥 COMPRAR AGORA 🔥</a>
"""

    enviar_telegram(mensagem)

    # ======================
    # ATUALIZA STATUS
    # ======================

    sheet.update_cell(row_number, col["STATUS"], "ENVIADO")

    data_postagem = datetime.now(
        ZoneInfo("America/Fortaleza")
    ).strftime("%d/%m/%Y %H:%M")

    sheet.update_cell(row_number, col["DATA POSTAGEM"], data_postagem)

    # ======================
    # CONFIG UPDATE CORRIGIDO
    # ======================

    atualizar_ultimo_envio()

    posts_enviados += 1
