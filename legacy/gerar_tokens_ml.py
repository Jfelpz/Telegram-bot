import json
import sys
from pathlib import Path

import requests

# ==========================================
# Adiciona a raiz do projeto ao Python Path
# ==========================================

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT))

from config import ML_CLIENT_ID, ML_CLIENT_SECRET


# ==========================================
# Arquivo PKCE
# ==========================================

PKCE_FILE = Path(__file__).parent / "pkce.json"

if not PKCE_FILE.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {PKCE_FILE}"
    )

with open(
    PKCE_FILE,
    "r",
    encoding="utf-8"
) as f:

    pkce = json.load(f)


# ==========================================
# Recebe o CODE
# ==========================================

code = input(
    "Cole aqui o CODE recebido:\n\n"
).strip()


# ==========================================
# Payload OAuth
# ==========================================

payload = {

    "grant_type": "authorization_code",

    "client_id": ML_CLIENT_ID,

    "client_secret": ML_CLIENT_SECRET,

    "code": code,

    "redirect_uri":
        "https://telegram-bot-ml-oauth.onrender.com/callback",

    "code_verifier":
        pkce["code_verifier"]

}


print("\nSolicitando tokens...\n")


# ==========================================
# Requisição
# ==========================================

r = requests.post(

    "https://api.mercadolibre.com/oauth/token",

    data=payload,

    timeout=30

)


print("Status:", r.status_code)


try:

    resposta = r.json()

    print(
        json.dumps(
            resposta,
            indent=4,
            ensure_ascii=False
        )
    )

except Exception:

    print(r.text)


# ==========================================
# Salvar Tokens
# ==========================================

if r.status_code == 200:

    TOKEN_FILE = ROOT / "ml_tokens.json"

    with open(
        TOKEN_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            resposta,
            f,
            indent=4,
            ensure_ascii=False
        )

    print()

    print("✅ Tokens gerados com sucesso!")

    print(f"Arquivo salvo em:\n{TOKEN_FILE}")

else:

    print()

    print("❌ Não foi possível gerar os tokens.")
