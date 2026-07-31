# =====================================================
# CONFIGURAÇÃO
# =====================================================

LINK_CANAL = "https://t.me/SEU_CANAL"

LOJAS_PIX = (
    "MAGALU",
    "MAGAZINE LUIZA",
    "MAGAZINEVOCÊ",
    "MAGAZINE VOCE",
    "MAGAZINE VOCÊ"
)


# =====================================================
# MONTA MENSAGEM DO TELEGRAM
# =====================================================

def montar_mensagem(produto, dados):

    nome = str(
        produto.get("PRODUTO", "")
    ).strip()

    categoria = str(
        produto.get("CATEGORIA", "")
    ).strip()

    loja = str(
        produto.get("LOJA", "")
    ).strip().upper()

    link = str(
        produto.get("LINK_AFILIADO", "")
    ).strip()

    preco = float(
        dados.get("preco", 0)
    )

    preco_antigo = float(
        dados.get("preco_antigo", 0)
    )

    preco_pix = float(
        dados.get("preco_pix", 0)
    )

    desconto = int(
        round(
            float(dados.get("desconto", 0))
        )
    )

    imagem = dados.get("imagem", "")

    mensagem = f"""
🔥 <b>OFERTA RELÂMPAGO</b>

🛒 <b>{nome}</b>

💸 <b>De:</b> R$ {preco_antigo:.2f}

💰 <b>Por:</b> R$ {preco:.2f}
"""

    # =====================================================
    # PREÇO PIX
    # Apenas Magalu e apenas se houver desconto adicional
    # =====================================================

    if (
        loja in LOJAS_PIX
        and preco_pix > 0
        and preco_pix < preco
    ):

        desconto_pix = int(
            round(
                ((preco - preco_pix) / preco) * 100
            )
        )

        mensagem += f"""
⚡ <b>No PIX:</b> R$ {preco_pix:.2f}
💳 <b>Economize mais {desconto_pix}% pagando via PIX</b>
"""

    mensagem += f"""

📉 <b>{desconto}% OFF</b>

🏷️ <b>Categoria:</b> {categoria}

🏪 <b>Loja:</b> {loja.title()}

━━━━━━━━━━━━━━━━━━

🚀 Aproveite antes que o preço aumente!

👉 <a href="{link}">🛒 COMPRAR AGORA</a>

━━━━━━━━━━━━━━━━━━

📢 Compartilhe essa oferta:
{LINK_CANAL}

━━━━━━━━━━━━━━━━━━

⚠️ Os preços podem ser alterados sem aviso.
"""

    return {

        "texto": mensagem.strip(),

        "imagem": imagem

    }
