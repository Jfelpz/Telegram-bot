import os

# ==================================================
# 🔐 CREDENCIAIS
# ==================================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SHEET_ID = os.getenv("SHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")


# ==================================================
# 🤖 BOT (PUBLICAÇÃO TELEGRAM)
# ==================================================
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 30))
DESCONTO_MINIMO = float(os.getenv("DESCONTO_MINIMO", 15))
LIMITE_POSTS = int(os.getenv("LIMITE_POSTS", 1))


# ==================================================
# 🧠 COLETOR (NOVA CAMADA)
# ==================================================

# Limite de produtos atualizados por execução (anti-bloqueio Amazon)
MAX_COLETAS = int(os.getenv("MAX_COLETAS", 8))

# Intervalo base (fallback caso cache não exista)
COLETA_MIN_MINUTOS = int(os.getenv("COLETA_MIN_MINUTOS", 60))
COLETA_MAX_MINUTOS = int(os.getenv("COLETA_MAX_MINUTOS", 90))


# ==================================================
# 🧠 CACHE (CONTROLE INTELIGENTE)
# ==================================================

# Segurança extra: tempo mínimo absoluto entre coletas (override do cache)
CACHE_MIN_ABSOLUTO = int(os.getenv("CACHE_MIN_ABSOLUTO", 30))


# ==================================================
# 📊 REGRAS FUTURAS DE RANKING
# (já preparando o ranking.py)
# ==================================================

DESCONTO_MIN_RANKING = float(os.getenv("DESCONTO_MIN_RANKING", 10))
PESO_DESCONTO = float(os.getenv("PESO_DESCONTO", 0.7))
PESO_RECENCIA = float(os.getenv("PESO_RECENCIA", 0.3))


# ==================================================
# ⚙️ SISTEMA GERAL
# ==================================================

AMBIENTE = os.getenv("AMBIENTE", "dev")  # dev | prod

DEBUG = AMBIENTE != "prod"
