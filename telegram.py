import requests

from config import TELEGRAM_TOKEN, CHAT_ID


# =====================================================
# ENVIA MENSAGEM PARA O TELEGRAM
# =====================================================

def enviar(texto, imagem=None):

    # =================================================
    # SE EXISTIR IMAGEM, USA sendPhoto
    # =================================================

    if imagem:

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

        payload = {

            "chat_id": CHAT_ID,

            "photo": imagem,

            "caption": texto,

            "parse_mode": "HTML"

        }

    # =================================================
    # CASO NÃO EXISTA IMAGEM
    # =================================================

    else:

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

        payload = {

            "chat_id": CHAT_ID,

            "text": texto,

            "parse_mode": "HTML",

            "disable_web_page_preview": False

        }

    # =================================================
    # ENVIO
    # =================================================

    response = requests.post(
        url,
        data=payload
    )

    print("📨 Telegram status:", response.status_code)

    if response.status_code != 200:

        print("❌ Erro Telegram:")

        print(response.text)

    return response
