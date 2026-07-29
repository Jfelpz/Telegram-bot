import requests

from config import TELEGRAM_TOKEN, CHAT_ID


def enviar(produto):
    """
    Envia uma promoção para o Telegram utilizando foto.
    """

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    legenda = f"""
🔥 <b>PROMOÇÃO</b>

📦 <b>{produto['PRODUTO']}</b>

💰 <b>Preço:</b> R$ {produto['PREÇO']}

🏷 <b>Desconto:</b> {produto['DESCONTO']}%

🏪 <b>Loja:</b> {produto['LOJA']}

🛒 <a href="{produto['LINK_AFILIADO']}">COMPRAR AGORA</a>

#promocao #{produto['LOJA'].lower()}
"""

    payload = {
        "chat_id": CHAT_ID,
        "photo": produto["IMAGEM"],
        "caption": legenda,
        "parse_mode": "HTML"
    }

    resposta = requests.post(url, data=payload)

    print(f"Telegram: {resposta.status_code}")

    if resposta.status_code != 200:
        print(resposta.text)

    return resposta
