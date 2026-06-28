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
# AUTH
# ==========================

SHEET_ID = os.getenv("SHEET_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

client = gspread.authorize(
    ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(GOOGLE_CREDENTIALS),
        scope
    )
)

spreadsheet = client.open_by_key(SHEET_ID)

sheet = spreadsheet.worksheet("MENU")
config_sheet = spreadsheet.worksheet("CONFIG")

# ==========================
# COLUNAS SEGURAS
# ==========================

header = [h.strip().upper() for h in sheet.row_values(1)]

def col_index(name):
    name = name.strip().upper()
    if name not in header:
        raise Exception(f"Coluna não existe: {name}")
    return header.index(name) + 1

# ==========================
# CONFIG
# ==========================

config = {
    row[0].strip().upper(): row[1]
    for row in config_sheet.get_all_values()
    if len(row) >= 2
}

INTERVALO = int(config.get("INTERVALO_MINUTOS", 30)) * 60
ULTIMO_ENVIO = float(config.get("ULTIMO_ENVIO", 0))
LIMITE_POSTS = int(config.get("LIMITE_POSTS", 1))
DESCONTO_MINIMO = float(config.get("DESCONTO_MINIMO", 15))
MODO_TESTE = str(config.get("MODO_TESTE", "FALSE")).upper() == "TRUE"

if not MODO_TESTE and (time.time() - ULTIMO_ENVIO < INTERVALO):
    print("⏳ Aguardando intervalo")
    exit()

# ==========================
# TELEGRAM
# ==========================

def enviar(msg):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": msg,
            "parse_mode": "HTML"
        }
    )

# ==========================
# LINHAS REAIS (CORRETO AGORA)
# ==========================

values = sheet.get_all_values()
header_row = [h.strip().upper() for h in values[0]]

def find_col(name):
    return header_row.index(name.strip().upper())

rows = []

for i in range(1, len(values)):
    row = values[i]
    rows.append((i + 1, row))  # linha real do Sheets

# ==========================
# ENVIO
# ==========================

enviados = 0

for row_number, row in rows:

    if enviados >= LIMITE_POSTS:
        break

    try:
        status = row[find_col("STATUS")].strip().upper()
        if status == "ENVIADO":
            continue

        produto = row[find_col("PRODUTO")]
        preco = row[find_col("PREÇO")]
        link = row[find_col("LINK_AFILIADO")]
        desconto = row[find_col("DESCONTO")]

    except:
        continue

    try:
        if float(desconto.replace("%", "").replace(",", ".")) < DESCONTO_MINIMO:
            continue
    except:
        pass

    # ID seguro
    id_col = find_col("ID")
    if not row[id_col]:
        produto_id = str(uuid.uuid4())[:8]
        sheet.update_cell(row_number, id_col + 1, produto_id)

    mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b> 🔥

⚡ <b>{produto}</b>

💰 R$ {preco}

👉 <a href="{link}">COMPRAR</a>
"""

    enviar(mensagem)

    # STATUS
    sheet.update_cell(row_number, find_col("STATUS") + 1, "ENVIADO")

    # DATA
    sheet.update_cell(
        row_number,
        find_col("DATA POSTAGEM") + 1,
        datetime.now(ZoneInfo("America/Fortaleza")).strftime("%d/%m/%Y %H:%M")
    )

    # CONFIG SAFE
    config_values = config_sheet.get_all_values()

    for i, r in enumerate(config_values, start=1):
        if r[0].strip().upper() == "ULTIMO_ENVIO":
            config_sheet.update_cell(i, 2, str(time.time()))
            break

    enviados += 1
