import uuid
import time
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

from config import (
    sheet,
    config_sheet,
    TELEGRAM_TOKEN,
    CHAT_ID
)

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

    # Ignora a primeira linha (cabeçalho)
    for row in values[1:]:
        if len(row) < 2:
            continue

        key = row[0].strip().upper()
        val = row[1].strip()

        cfg[key] = val

    return cfg

config = load_config()

def set_config(chave, valor):
    values = config_sheet.get_all_values()

    # Começa na linha 2 porque a linha 1 é o cabeçalho
    for linha, row in enumerate(values[1:], start=2):

        if len(row) < 2:
            continue

        if row[0].strip().upper() == chave.strip().upper():

            config_sheet.update_cell(
                linha,
                2,
                str(valor)
            )

            return

    raise Exception(
        f"Configuração '{chave}' não encontrada."
    )

ULTIMO_ENVIO = safe_int(config.get("ULTIMO_ENVIO", 0))
INTERVALO = safe_int(config.get("INTERVALO_MINUTOS", 30)) * 60
LIMITE_POSTS = safe_int(config.get("LIMITE_POSTS", 1))

try:
    DESCONTO_MINIMO = float(
        str(config.get("DESCONTO_MINIMO", 15)).replace(",", ".")
    )
except:
    DESCONTO_MINIMO = 15

MODO_TESTE = (
    str(config.get("MODO_TESTE", "FALSE"))
    .strip()
    .upper() == "TRUE"
)
# ==========================
# CONTROLE DE TEMPO
# ==========================

agora = int(time.time())

if not MODO_TESTE and (agora - ULTIMO_ENVIO < INTERVALO):
    print("⏳ Intervalo ativo, mas script continua sem enviar.")
    enviou_permitido = False
else:
    enviou_permitido = True

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
print("📊 TOTAL LINHAS BRUTAS:", len(values))
print("📊 HEADER:", values[0])
header_row = [h.strip().upper() for h in values[0]]

def col(name):
    return header_row.index(name.strip().upper())

rows = [(i + 1, values[i]) for i in range(1, len(values))]

# ==========================
# ENVIO
# ==========================

enviados = 0

if not enviou_permitido:
    print("⏳ Bloqueado pelo intervalo de tempo.")
    exit()
print("🔁 ENTRANDO NO LOOP DE LINHAS")
print("🔁 TOTAL ROWS:", len(rows))    
for row_number, row in rows:
    print("🔄 LENDO LINHA:", row_number)
    if enviados >= LIMITE_POSTS:
        break

    try:
        status_raw = row[col("STATUS")] or ""
        status = str(status_raw).strip().upper()
        if status == "ENVIADO":
            continue

        produto = row[col("PRODUTO")]
        preco = row[col("PREÇO")]
        link = row[col("LINK_AFILIADO")]
        desconto = row[col("DESCONTO")]

    except Exception as e:
        print("❌ ERRO NA LINHA", row_number, e)
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
    print("📤 ENVIANDO PRODUTO:", produto)
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

    set_config(
    "ULTIMO_ENVIO",
    int(time.time())
)

set_config(
    "ULTIMA_POSTAGEM",
    datetime.now(
        ZoneInfo("America/Fortaleza")
    ).strftime("%d/%m/%Y %H:%M")
)

enviados += 1
