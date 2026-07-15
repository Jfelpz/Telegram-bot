# =====================================================
# MONTA MENSAGEM DO TELEGRAM
# =====================================================

def montar_mensagem(produto):

    nome = str(produto.get("PRODUTO", "")).strip()

    preco = str(produto.get("PREÇO", "")).strip()

    preco_antigo = str(
        produto.get("PREÇO_ANTIGO", "")
    ).strip()

    desconto = str(
        produto.get("DESCONTO", "")
    ).strip()

    categoria = str(
        produto.get("CATEGORIA", "")
    ).strip()

    loja = str(
        produto.get("LOJA", "")
    ).strip()

    link = str(
        produto.get("LINK_AFILIADO", "")
    ).strip()

    mensagem = f"""
🔥 <b>🔥 OFERTA RELÂMPAGO 🔥</b>

🛒 <b>{nome}</b>

"""

    if preco_antigo:

        mensagem += f"💸 <b>De:</b> {preco_antigo}\n"

    mensagem += f"""
💰 <b>Por:</b> {preco}

📉 <b>Desconto:</b> {desconto}

🏷️ <b>Categoria:</b> {categoria}

🏪 <b>Loja:</b> {loja}

━━━━━━━━━━━━━━━━━━

⚡ Estoque pode acabar a qualquer momento.

🚀 Aproveite enquanto o preço está disponível!

👉 <a href="{link}">🛒 COMPRAR AGORA</a>

━━━━━━━━━━━━━━━━━━

⚠️ Os preços podem sofrer alterações sem aviso.
"""

    return mensagem
