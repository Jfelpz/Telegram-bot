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

def calcular_score(row):
    score = 0
    
    prioridade = str(row.get("PRIORIDADE", "")).strip().upper()
    desconto = str(row.get("DESCONTO", "")).replace("%", "").strip()
    categoria = str(row.get("CATEGORIA", "")).strip().upper()
    
    try:
        desconto = float(desconto)
    except:
        desconto = 0
    
    # Prioridade
    if prioridade == "ALTA":
        score += 20
    elif prioridade == "MEDIA":
        score += 10
    elif prioridade == "BAIXA":
        score += 5
    
    # Desconto
    score += desconto
    
    # Categorias premium
    categorias_premium = [
        "GPU",
        "PLACA DE VIDEO",
        "PROCESSADOR",
        "SSD"
    ]
    
    if categoria in categorias_premium:
        score += 10
    
    return score
    #Ordena por score
    
    data.sort(key=calcular_score, reverse=True)
    
    posts_enviados = 0
    limite = 1
    
    for i, row in enumerate(data, start=2):
    
    if posts_enviados >= limite:
        break
    
    if str(row.get("STATUS", "")).strip().upper() == "ENVIADO":
        continue
    
    produto = row.get("PRODUTO")
    preco = row.get("PREÇO")
    link = row.get("LINK_AFILIADO")
    
    preco_antigo = str(row.get("PREÇO_ANTIGO", "")).strip()
    desconto = str(row.get("DESCONTO", "")).strip()
    loja = str(row.get("LOJA", "")).strip()
    categoria = str(row.get("CATEGORIA", "")).strip()
    
    prioridade = str(row.get("PRIORIDADE", "")).strip().upper()
    
    try:
        desconto_valor = float(desconto.replace("%", "").strip() or 0)
    except:
        desconto_valor = 0
    
    # Data de adição
    data_adicao = str(row.get("DATA_ADIÇÃO", "")).strip()
    
    if not data_adicao:
        data_adicao = datetime.now(
            ZoneInfo("America/Fortaleza")
        ).strftime("%d/%m/%Y %H:%M")
    
        sheet.update_cell(i, 11, data_adicao)
    
    # Filtro de qualidade
    if prioridade != "ALTA" and desconto_valor < 15:
        continue
    
    mensagem = f"""
    
    🔥 OFERTA RELÂMPAGO 🔥
    
    ⚡ {produto}
    
    🏪 Loja: {loja}
    📂 Categoria: {categoria}
    
    💰 Preço atual: R$ {preco}
    """
    
    if preco_antigo:
        mensagem += f"\n💸 <b>De:</b> R$ {preco_antigo}"
    
    if desconto:
        mensagem += f"\n📉 <b>Desconto:</b> {desconto}"
    
    mensagem += f"""
    
    ━━━━━━━━━━━━━━━
    
    ⏳ ATENÇÃO: oferta pode acabar a qualquer momento
    
    📦 Estoque limitado — alta demanda
    
    🚀 Não perca essa oportunidade
    
    👉 🔥 COMPRAR AGORA 🔥
    
    #promoção #hardware #oferta
    """
    
    enviar_telegram(mensagem)
    
    sheet.update_cell(i, 5, "ENVIADO")
    
    data_postagem = datetime.now(
        ZoneInfo("America/Fortaleza")
    ).strftime("%d/%m/%Y %H:%M")
    
    sheet.update_cell(i, 12, data_postagem)
    
    posts_enviados += 1
