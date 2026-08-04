import os

# ==================================================
# 🔐 CREDENCIAIS
# ==================================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")


# ==================================================
# ⚙️ MERCADO LIVRE
# ==================================================

ML_CLIENT_ID = os.getenv(
    "ML_CLIENT_ID",
    "3055663592267864"
)

ML_CLIENT_SECRET = os.getenv(
    "ML_CLIENT_SECRET",
    "y9CoTMn9A0dVSVVNcORAuLvCyYCWd6wE"
)

ML_ACCESS_TOKEN = os.getenv("ML_ACCESS_TOKEN")
ML_REFRESH_TOKEN = os.getenv("ML_REFRESH_TOKEN")


# ==================================================
# 🌐 SCRAPER API
# ==================================================

SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")

SCRAPER_TIMEOUT = int(
    os.getenv("SCRAPER_TIMEOUT", 60)
)

SCRAPER_RETRIES = int(
    os.getenv("SCRAPER_RETRIES", 3)
)


# ==================================================
# 🤖 BOT
# ==================================================

INTERVALO_MINUTOS = int(
    os.getenv("INTERVALO_MINUTOS", 30)
)

DESCONTO_MINIMO = float(
    os.getenv("DESCONTO_MINIMO", 15)
)


# ==================================================
# 🧠 COLETOR
# ==================================================

MAX_COLETAS = int(
    os.getenv("MAX_COLETAS", 8)
)

COLETA_MIN_MINUTOS = int(
    os.getenv("COLETA_MIN_MINUTOS", 60)
)

COLETA_MAX_MINUTOS = int(
    os.getenv("COLETA_MAX_MINUTOS", 90)
)


# ==================================================
# 🧠 CACHE
# ==================================================

CACHE_MIN_ABSOLUTO = int(
    os.getenv("CACHE_MIN_ABSOLUTO", 30)
)


# ==================================================
# 📊 RANKING
# ==================================================

DESCONTO_MIN_RANKING = float(
    os.getenv("DESCONTO_MIN_RANKING", 10)
)

PESO_DESCONTO = float(
    os.getenv("PESO_DESCONTO", 0.7)
)

PESO_RECENCIA = float(
    os.getenv("PESO_RECENCIA", 0.3)
)


# ==================================================
# ⚙️ SISTEMA
# ==================================================

AMBIENTE = os.getenv(
    "AMBIENTE",
    "dev"
)

DEBUG = AMBIENTE.lower() != "prod"
