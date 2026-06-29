import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")


# ==========================
# CONFIG DO BOT
# ==========================

INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 30))
DESCONTO_MINIMO = float(os.getenv("DESCONTO_MINIMO", 15))
LIMITE_POSTS = int(os.getenv("LIMITE_POSTS", 1))
