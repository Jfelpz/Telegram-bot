import uuid
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from sheets import sheet
from config import INTERVALO_MINUTOS, DESCONTO_MINIMO, LIMITE_POSTS
from sheets import config_sheet


def processar(enviar):

    values = sheet.get_all_values()
    header = [h.strip().upper() for h in values[0]]

    def col(name):
        return header.index(name.strip().upper())

    rows = [(i + 1, values[i]) for i in range(1, len(values))]

    enviados = 0

    for row_number, row in rows:

        if enviados >= LIMITE_POSTS:
            break
    
        try:
            status = str(row[col("STATUS")] or "").strip().upper()
    
            if status == "ENVIADO":
                continue
    
            produto = row[col("PRODUTO")]
            preco = row[col("PREÇO")]
            link = row[col("LINK_AFILIADO")]
            desconto = row[col("DESCONTO")]
    
        except Exception as e:
            print("❌ ERRO LINHA", row_number, e)
            continue
    
        # 👇 AQUI (MESMO NÍVEL DOS OUTROS BLOCOS)
        id_col = col("ID")
    
        if not row[id_col]:
            produto_id = str(uuid.uuid4())[:8]
            sheet.update_cell(row_number, id_col + 1, produto_id)
            print("🆔 ID GERADO:", produto_id)
    
        try:
            desconto_valor = float(
                str(desconto).replace("%", "").replace(",", ".")
            )
        except:
            desconto_valor = 0
    
        if desconto_valor < DESCONTO_MINIMO:
            continue

        mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b> 🔥

⚡ <b>{produto}</b>

💰 R$ {preco}

👉 <a href="{link}">COMPRAR AGORA</a>
"""

        print("📤 ENVIANDO:", produto)
        enviar(mensagem)

        sheet.update_cell(row_number, col("STATUS") + 1, "ENVIADO")

        sheet.update_cell(
            row_number,
            col("DATA_POSTAGEM") + 1,
            datetime.now(ZoneInfo("America/Fortaleza")).strftime("%d/%m/%Y %H:%M")
        )

        enviados += 1

        break
