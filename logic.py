import uuid
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from sheets import sheet
from config import LIMITE_POSTS


def processar(enviar):

    values = sheet.get_all_values()
    header = [h.strip().upper() for h in values[0]]

    def col(name):
        return header.index(name.strip().upper())

    rows = [(i + 1, values[i]) for i in range(1, len(values))]

    # 🔒 pega apenas pendentes
    pendentes = []
    for row_number, row in rows:
        try:
            status = str(row[col("STATUS")] or "").strip().upper()
            if status != "ENVIADO":
                pendentes.append((row_number, row))
        except:
            continue

    # 🔀 embaralha para evitar padrão fixo
    random.shuffle(pendentes)

    # 🔒 limite por execução (batch seguro)
    BATCH_LIMIT = min(3, LIMITE_POSTS)
    pendentes = pendentes[:BATCH_LIMIT]

    enviados = 0

    for row_number, row in pendentes:

        if enviados >= LIMITE_POSTS:
            break

        try:
            produto = row[col("PRODUTO")]
            preco = row[col("PREÇO")]
            link = row[col("LINK_AFILIADO")]
            desconto = row[col("DESCONTO")]
        except Exception as e:
            print("❌ ERRO LINHA", row_number, e)
            continue

        # 🆔 cria ID se não existir
        id_col = col("ID")

        if not row[id_col]:
            produto_id = str(uuid.uuid4())[:8]
            sheet.update_cell(row_number, id_col + 1, produto_id)
            print("🆔 ID GERADO:", produto_id)

        # 💰 tratamento de desconto
        try:
            desconto_valor = float(
                str(desconto).replace("%", "").replace(",", ".")
            )
        except:
            desconto_valor = 0

        # 🚫 filtro de desconto mínimo (se existir no config futuramente)
        if desconto_valor <= 0:
            continue

        # 📢 mensagem final
        mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b> 🔥

⚡ <b>{produto}</b>

💰 R$ {preco}

📉 Desconto: {desconto}

👉 <a href="{link}">COMPRAR AGORA</a>
"""

        print("📤 ENVIANDO:", produto)

        try:
            enviar(mensagem)
        except Exception as e:
            print("❌ ERRO ENVIO TELEGRAM:", e)
            continue

        # ✅ marca como enviado
        sheet.update_cell(row_number, col("STATUS") + 1, "ENVIADO")

        sheet.update_cell(
            row_number,
            col("DATA_POSTAGEM") + 1,
            datetime.now(ZoneInfo("America/Fortaleza")).strftime("%d/%m/%Y %H:%M")
        )

        enviados += 1
