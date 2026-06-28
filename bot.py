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
# CONFIGURAÇÕES GERAIS
# ==========================

SHEET_ID = os.getenv("SHEET_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# ==========================
# CONEXÃO GOOGLE SHEETS
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
# LER CONFIG (CORRIGIDO)
# ==========================

config_raw = config_sheet.get_all_records()

config = {}
for row in config_raw:
    key = str(row.get("CONFIGURAÇÃO", "")).strip().upper()
    value = row.get("VALOR")
    config[key] = value

# Conversões seguras
INTERVALO_MINUTOS = int(config.get("INTERVALO_MINUTOS", 30))
INTERVALO = INTERVALO_MINUTOS * 60

LIMITE_POSTS = int(config.get("LIMITE_POSTS", 1))
SCORE_MINIMO = int(config.get("SCORE_MINIMO", 15))
MAX_POSTS_DIA = int(config.get("MAX_POSTS_DIA", 48))
DESCONTO_MINIMO = float(config.get("DESCONTO_MINIMO", 15))

ULTIMO_ENVIO = float(config.get("ULTIMO_ENVIO", 0))
MODO_TESTE = str(config.get("MODO_TESTE", "FALSE")).upper() == "TRUE"

# ==========================
# CONTROLE DE TEMPO
# ==========================

agora = time.time()

if not MODO_TESTE and (agora - ULTIMO_ENVIO < INTERVALO):
    print("⏳ Ainda não passou o intervalo.")
    exit()

# ==========================
# DADOS DA PLANILHA
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
# ORDENAÇÃO
# ==========================

rows.sort(key=lambda x: calcular_score(x[1]), reverse=True)

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
    prioridade = str(row.get("PRIORIDADE", "")).strip().upper()

    try:
        desconto_valor = float(desconto.replace("%", "").replace(",", "."))
    except:
        desconto_valor = 0

    # filtro mínimo vindo da CONFIG
    if desconto_valor < DESCONTO_MINIMO:
        continue

    if prioridade != "ALTA" and desconto_valor < DESCONTO_MINIMO:
        continue

    # ======================
    # ID
    # ======================

    produto_id = str(row.get("ID", "")).strip()

    if not produto_id:
        produto_id = str(uuid.uuid4())[:8]

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

💰 <b>Preço:</b> R$ {preco}

👉 <a href="{link}">🔥 COMPRAR AGORA 🔥</a>
"""

    enviar_telegram(mensagem)

    # ======================
    # ATUALIZA STATUS
    # ======================

    if row_number > 1:
        sheet.update_cell(row_number, 5, "ENVIADO")

    data_postagem = datetime.now(
        ZoneInfo("America/Fortaleza")
    ).strftime("%d/%m/%Y %H:%M")

    if row_number > 1:
        sheet.update_cell(row_number, 13, data_postagem)

    # ======================
    # ATUALIZA ULTIMO ENVIO
    # ======================

    config_data = config_sheet.get_all_values()

for i, row in enumerate(config_data, start=1):
    if row[0].strip().upper() == "ULTIMO_ENVIO":
        config_sheet.update_cell(i, 2, str(time.time()))
        break

    posts_enviados += 1
