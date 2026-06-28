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

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(GOOGLE_CREDENTIALS),
    scope
)

client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SHEET_ID)

sheet = spreadsheet.worksheet("MENU")
config_sheet = spreadsheet.worksheet("CONFIG")

# ==========================
# COLUNAS SEGURAS
# ==========================

header = sheet.row_values(1)

col = {
    str(name).strip().upper(): idx + 1
    for idx, name in enumerate(header)
}

# ==========================
# FUNÇÃO SEGURA DE UPDATE
# ==========================

def atualizar_campo(linha, nome_coluna, valor):
    nome_coluna = nome_coluna.strip().upper()

    if nome_coluna not in col:
        print(f"⚠️ Coluna não encontrada: {nome_coluna}")
        return

    sheet.update_cell(linha, col[nome_coluna], valor)

# ==========================
# CONFIG SEGURA
# ==========================

config_values = config_sheet.get_all_values()

config = {}

for row in config_values:
    if len(row) < 2:
        continue
    config[row[0].strip().upper()] = row[1]

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
    print("⏳ Aguardando intervalo...")
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
# CONFIG UPDATE SEGURO
# ==========================

def atualizar_ultimo_envio():
    values = config_sheet.get_all_values()

    for i, row in enumerate(values, start=1):
        if len(row) > 0 and row[0].strip().upper() == "ULTIMO_ENVIO":
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

    try:
        desconto_valor = float(desconto.replace("%", "").replace(",", "."))
    except:
        desconto_valor = 0

    if desconto_valor < DESCONTO_MINIMO:
        continue

    loja = row.get("LOJA", "")
    categoria = row.get("CATEGORIA", "")

    # ======================
    # ID SEGURO
    # ======================

    if not row.get("ID"):
        produto_id = str(uuid.uuid4())[:8]
        atualizar_campo(row_number, "ID", produto_id)

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
    # STATUS
    # ======================

    atualizar_campo(row_number, "STATUS", "ENVIADO")

    data_postagem = datetime.now(
        ZoneInfo("America/Fortaleza")
    ).strftime("%d/%m/%Y %H:%M")

    atualizar_campo(row_number, "DATA POSTAGEM", data_postagem)

    # ======================
    # CONFIG
    # ======================

    atualizar_ultimo_envio()

    posts_enviados += 1
