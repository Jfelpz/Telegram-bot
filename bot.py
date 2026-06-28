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

def find_col(name):
    return header.index(name.strip().upper())

# ==========================
# CONFIG (BLINDADA)
# ==========================

def safe_int(value):
    try:
        return int(str(value).replace(".", "").replace(",", "").strip())
    except:
        return 0

def load_config():
    values = config_sheet.get_all_values()
    cfg = {}

    for row in values:
        if len(row) < 2:
            continue
        key = row[0].strip().upper()
        val = row[1]
        cfg[key] = val

    return cfg

config = load_config()

ULTIMO_ENVIO = safe_int(config.get("ULTIMO_ENVIO", 0))
INTERVALO = int(config.get("INTERVALO_MINUTOS", 30)) * 60
LIMITE_POSTS = int(config.get("LIMITE_POSTS", 1))
DESCONTO_MINIMO = float(config.get("DESCONTO_MINIMO", 15))
MODO_TESTE = str(config.get("MODO_TESTE", "FALSE")).upper() == "TRUE"

# ==========================
# CONTROLE DE TEMPO
# ==========================

agora = int(time.time())

if not MODO_TESTE and (agora - ULTIMO_ENVIO < INTERVALO):
    print("⏳ Aguardando intervalo...")
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
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    )

# ==========================
# DADOS
# ==========================

values = sheet.get_all_values()
header_row = [h.strip().upper() for h in values[0]]

def col(name):
    return header_row.index(name.strip().upper())

rows = [(i + 1, values[i]) for i in range(1, len(values))]

# ==========================
# ENVIO
# ==========================

enviados = 0

for row_number, row in rows:

    if enviados >= LIMITE_POSTS:
        break

    try:
        status = row[col("STATUS")].strip().upper()
        if status == "ENVIADO":
            continue

        produto = row[col("PRODUTO")]
        preco = row[col("PREÇO")]
        link = row[col("LINK_AFILIADO")]
        desconto = row[col("DESCONTO")]

    except:
        continue

    try:
        desconto_valor = float(
            desconto.replace("%", "").replace(",", ".")
        )
    except:
        desconto_valor = 0

    if desconto_valor < DESCONTO_MINIMO:
        continue

    # ======================
    # ID
    # ======================

    id_col = col("ID")

    if not row[id_col]:
        produto_id = str(uuid.uuid4())[:8]
        sheet.update_cell(row_number, id_col + 1, produto_id)

    # ======================
    # MENSAGEM
    # ======================

    mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b> 🔥

⚡ <b>{produto}</b>

💰 R$ {preco}

👉 <a href="{link}">COMPRAR AGORA</a>
"""

    enviar(mensagem)

    # ======================
    # STATUS
    # ======================

    sheet.update_cell(row_number, col("STATUS") + 1, "ENVIADO")

    sheet.update_cell(
        row_number,
        col("DATA_POSTAGEM") + 1,
        datetime.now(ZoneInfo("America/Fortaleza")).strftime("%d/%m/%Y %H:%M")
    )

    # ======================
    # CONFIG (CORREÇÃO FINAL)
    # ======================

    config_sheet.update_cell(
        1,
        2,
        str(int(time.time()))
    )

    enviados += 1
