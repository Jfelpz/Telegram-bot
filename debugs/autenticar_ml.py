"""
=========================================================
AUTENTICADOR MERCADO LIVRE
Parte 1 - PKCE + URL de autorização
=========================================================
"""

import json
import base64
import hashlib
import secrets
import webbrowser

from pathlib import Path
from urllib.parse import urlencode

from config import ML_CLIENT_ID


# =========================================================
# CONFIGURAÇÕES
# =========================================================

REDIRECT_URI = "https://telegram-bot-jfelps.onrender.com/callback"

AUTH_URL = "https://auth.mercadolivre.com.br/authorization"

ARQUIVO_PKCE = Path("debugs/pkce.json")


# =========================================================
# GERAR CODE VERIFIER
# =========================================================

def gerar_code_verifier():

    return secrets.token_urlsafe(64)


# =========================================================
# GERAR CODE CHALLENGE
# =========================================================

def gerar_code_challenge(code_verifier):

    digest = hashlib.sha256(
        code_verifier.encode("utf-8")
    ).digest()

    return (
        base64.urlsafe_b64encode(digest)
        .decode("utf-8")
        .replace("=", "")
    )


# =========================================================
# GERAR STATE
# =========================================================

def gerar_state():

    return secrets.token_hex(16)


# =========================================================
# SALVAR DADOS
# =========================================================

def salvar_pkce(code_verifier, state):

    dados = {

        "code_verifier": code_verifier,

        "state": state

    }

    ARQUIVO_PKCE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(

        ARQUIVO_PKCE,

        "w",

        encoding="utf-8"

    ) as arquivo:

        json.dump(

            dados,

            arquivo,

            indent=4,

            ensure_ascii=False

        )


# =========================================================
# CARREGAR DADOS
# =========================================================

def carregar_pkce():

    if not ARQUIVO_PKCE.exists():

        return None

    with open(

        ARQUIVO_PKCE,

        "r",

        encoding="utf-8"

    ) as arquivo:

        return json.load(arquivo)


# =========================================================
# GERAR URL
# =========================================================

def gerar_url():

    verifier = gerar_code_verifier()

    challenge = gerar_code_challenge(verifier)

    state = gerar_state()

    salvar_pkce(verifier, state)

    parametros = {

        "response_type": "code",

        "client_id": ML_CLIENT_ID,

        "redirect_uri": REDIRECT_URI,

        "code_challenge": challenge,

        "code_challenge_method": "S256",

        "state": state

    }

    return f"{AUTH_URL}?{urlencode(parametros)}"


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AUTENTICADOR MERCADO LIVRE")
    print("=" * 70)

    url = gerar_url()

    print()
    print("Abra a URL abaixo:")
    print()
    print(url)
    print()

    try:

        webbrowser.open(url)

        print("Navegador aberto.")

    except Exception:

        print("Abra manualmente a URL acima.")

    print()
    print("Após autorizar o aplicativo, copie o parâmetro CODE.")
