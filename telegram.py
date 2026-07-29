import requests
from config import TELEGRAM_TOKEN, CHAT_ID

def enviar(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    response = requests.post(url, data=payload)

    # Debug opcional (ajuda muito se algo falhar)
    print("📨 Telegram status:", response.status_code)

    if response.status_code != 200:
        print("❌ Erro Telegram:", response.text)

    return response
