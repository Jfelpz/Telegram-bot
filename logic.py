import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from sheets import sheet
from config import (
    LIMITE_POSTS,
    DESCONTO_MINIMO
)

from ranking import gerar_ranking


FUSO = ZoneInfo("America/Fortaleza")


def processar(enviar):

    print("📋 Lendo planilha...")

    values = sheet.get_all_values()

    if len(values) <= 1:
        print("Nenhum produto encontrado.")
        return

    header = [h.strip().upper() for h in values[0]]

    # -----------------------------------------
    # Localiza colunas pelo nome
    # -----------------------------------------

    def col(nome):
        return header.index(nome.strip().upper())

    # -----------------------------------------
    # Converte linhas em dicionários
    # -----------------------------------------

    produtos = []

    for row_number, row in enumerate(values[1:], start=2):

        produto = {}

        for i, coluna in enumerate(header):

            produto[coluna] = row[i] if i < len(row) else ""

        produto["ROW_NUMBER"] = row_number

        produtos.append(produto)

    # -----------------------------------------
    # Gera Ranking
    # -----------------------------------------

    ranking = gerar_ranking(produtos)

    print(f"Produtos elegíveis: {len(ranking)}")

    enviados = 0

    # -----------------------------------------
    # Percorre ranking
    # -----------------------------------------

    for produto in ranking:

        if enviados >= LIMITE_POSTS:
            break

        row = produto["ROW_NUMBER"]

        nome = produto.get("PRODUTO", "")
        preco = produto.get("PREÇO", "")
        preco_antigo = produto.get("PREÇO_ANTIGO", "")
        desconto = produto.get("DESCONTO", "")
        categoria = produto.get("CATEGORIA", "")
        loja = produto.get("LOJA", "")
        link = produto.get("LINK_AFILIADO", "")

        # -----------------------------------------
        # Desconto mínimo
        # -----------------------------------------

        try:

            desconto_float = float(
                str(desconto)
                .replace("%", "")
                .replace(",", ".")
            )

        except:

            desconto_float = 0

        if desconto_float < DESCONTO_MINIMO:

            print(
                f"⏩ Ignorado ({nome}) - desconto abaixo do mínimo."
            )

            continue

        # -----------------------------------------
        # Gera ID
        # -----------------------------------------

        if not produto.get("ID"):

            novo_id = str(uuid.uuid4())[:8]

            sheet.update_cell(
                row,
                col("ID") + 1,
                novo_id
            )

            print(
                f"🆔 ID criado para {nome}"
            )

        # -----------------------------------------
        # Monta mensagem
        # -----------------------------------------

        mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b> 🔥

🛒 <b>{nome}</b>

💰 <b>Preço:</b> {preco}

"""

        if preco_antigo:

            mensagem += f"💸 <b>Preço anterior:</b> {preco_antigo}\n"

        mensagem += f"""

📉 <b>Desconto:</b> {desconto}

🏷️ <b>Categoria:</b> {categoria}

🏪 <b>Loja:</b> {loja}

👉 <a href="{link}">🛒 COMPRAR AGORA</a>

⚠️ Os preços podem mudar a qualquer momento.
"""

        # -----------------------------------------
        # Envia Telegram
        # -----------------------------------------

        print(f"📤 Enviando: {nome}")

        try:

            enviar(mensagem)

        except Exception as erro:

            print(f"❌ Telegram: {erro}")

            continue

        # -----------------------------------------
        # Atualiza planilha
        # -----------------------------------------

        sheet.update_cell(
            row,
            col("STATUS") + 1,
            "ENVIADO"
        )

        sheet.update_cell(
            row,
            col("DATA_POSTAGEM") + 1,
            datetime.now(FUSO).strftime("%d/%m/%Y %H:%M")
        )

        enviados += 1

        print(f"✅ Publicado: {nome}")

    print(f"\n🎉 Processo finalizado. {enviados} produto(s) enviado(s).")
