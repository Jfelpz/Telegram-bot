# ==================================================
# MONTA MENSAGEM DO TELEGRAM
# ==================================================

def montar_mensagem(produto):

    nome = produto.get(
        "PRODUTO",
        ""
    )

    preco = produto.get(
        "PREÇO",
        ""
    )

    preco_antigo = produto.get(
        "PREÇO_ANTIGO",
        ""
    )

    desconto = produto.get(
        "DESCONTO",
        ""
    )

    categoria = produto.get(
        "CATEGORIA",
        ""
    )

    loja = produto.get(
        "LOJA",
        ""
    )

    link = produto.get(
        "LINK_AFILIADO",
        ""
    )

    mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b> 🔥

🛒 <b>{nome}</b>

💰 <b>Preço:</b> {preco}
"""

    if preco_antigo:

        mensagem += (
            f"\n💸 <b>De:</b> {preco_antigo}"
        )

    if desconto:

        mensagem += (
            f"\n📉 <b>Desconto:</b> {desconto}"
        )

    mensagem += f"""

🏷️ <b>Categoria:</b> {categoria}

🏪 <b>Loja:</b> {loja}

━━━━━━━━━━━━━━━━━━

⚡ Promoção por tempo limitado!

🚚 Produto disponível para compra.

👉 <a href="{link}">
🛒 COMPRAR AGORA
</a>

⚠️ O preço pode ser alterado a qualquer momento sem aviso.
"""

    return mensagem


# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    exemplo = {

        "PRODUTO": "RTX 5070",

        "PREÇO": "R$ 3.899,00",

        "PREÇO_ANTIGO": "R$ 4.599,00",

        "DESCONTO": "15%",

        "CATEGORIA": "GPU",

        "LOJA": "Amazon",

        "LINK_AFILIADO": "https://..."
    }

    print(
        montar_mensagem(
            exemplo
        )
    )
