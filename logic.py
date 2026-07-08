import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from sheets import sheet
from config import (
    LIMITE_POSTS,
    DESCONTO_MINIMO
)

from ranking import gerar_ranking


def processar(enviar):

    values = sheet.get_all_values()

    header = [h.strip().upper() for h in values[0]]

    def col(nome):
        return header.index(nome.strip().upper())

    produtos = []

    # ==================================================
    # MONTA DICIONÁRIOS DOS PRODUTOS
    # ==================================================

    for row_number, row in enumerate(values[1:], start=2):

        produto = {}

        for i, coluna in enumerate(header):

            produto[coluna] = row[i] if i < len(row) else ""

        produto["ROW_NUMBER"] = row_number

        produtos.append(produto)

    # ==================================================
    # GERA RANKING
    # ==================================================

    ranking = gerar_ranking(produtos)

    enviados = 0

    for produto in ranking:

        if enviados >= LIMITE_POSTS:
            break

        row_number = produto["ROW_NUMBER"]

        try:

            nome = produto["PRODUTO"]
            preco = produto["PREÇO"]
            link = produto["LINK_AFILIADO"]
            desconto = produto["DESCONTO"]

        except Exception as erro:

            print(f"❌ Erro linha {row_number}: {erro}")

            continue

        # ==================================================
        # DESCONTO
        # ==================================================

        try:

            desconto_valor = float(
                str(desconto)
                .replace("%", "")
                .replace(",", ".")
            )

        except:

            desconto_valor = 0


        if desconto_valor < DESCONTO_MINIMO:

            print(
                f"⏩ {nome} ignorado (desconto {desconto_valor}%)."
            )

            continue


        # ==================================================
        # GERA ID
        # ==================================================

        if not produto["ID"]:

            novo_id = str(uuid.uuid4())[:8]

            sheet.update_cell(
                row_number,
                col("ID") + 1,
                novo_id
            )

            print(
                f"🆔 ID criado para {nome}"
            )


        # ==================================================
        # MENSAGEM
        # ==================================================

        mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b>

🛒 <b>{nome}</b>

💰 <b>Preço:</b> R$ {preco}

📉 <b>Desconto:</b> {desconto}

🏷️ <b>Categoria:</b> {produto['CATEGORIA']}

🏪 <b>Loja:</b> {produto['LOJA']}

👉 <a href="{link}">COMPRAR AGORA</a>

⚠️ Os preços podem ser alterados a qualquer momento.
"""


        print(f"📤 Enviando: {nome}")

        try:

            enviar(mensagem)

        except Exception as erro:

            print(f"❌ Telegram: {erro}")

            continue


        # ==================================================
        # ATUALIZA PLANILHA
        # ==================================================

        sheet.update_cell(
            row_number,
            col("STATUS") + 1,
            "ENVIADO"
        )

        sheet.update_cell(
            row_number,
            col("DATA_POSTAGEM") + 1,
            datetime.now(
                ZoneInfo("America/Fortaleza")
            ).strftime("%d/%m/%Y %H:%M")
        )

        enviados += 1

    print(f"✅ {enviados} produto(s) enviado(s).")
