"""
=========================================================
AUTENTICADOR MERCADO LIVRE
Parte 1 - PKCE + URL de autorização
=========================================================
"""

import sys
import json
import base64
import hashlib
import secrets
import webbrowser

from pathlib import Path
from urllib.parse import urlencode

# =========================================================
# AJUSTA O PATH PARA FUNCIONAR NO GITHUB ACTIONS
# =========================================================

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# =========================================================
# IMPORTA CONFIGURAÇÕES
# =========================================================

from config import ML_CLIENT_ID


# =========================================================
# CONFIGURAÇÕES
# =========================================================

REDIRECT_URI = "https://telegram-bot-jfelps.onrender.com/callback"

AUTH_URL = "https://auth.mercadolivre.com.br/authorization"

ARQUIVO_PKCE = ROOT / "debugs" / "pkce.json"


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

# =========================================================
# PARTE 2
# TROCAR CODE POR ACCESS TOKEN
# =========================================================

import requests

from config import ML_CLIENT_SECRET


TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

ARQUIVO_TOKEN = Path("debugs/tokens_ml.json")


# =========================================================
# SALVAR TOKENS
# =========================================================

def salvar_tokens(tokens):

    ARQUIVO_TOKEN.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        ARQUIVO_TOKEN,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            tokens,
            arquivo,
            indent=4,
            ensure_ascii=False
        )


# =========================================================
# TROCAR CODE PELO TOKEN
# =========================================================

def trocar_code_por_token(code):

    pkce = carregar_pkce()

    if pkce is None:

        print("PKCE não encontrado.")
        return


    payload = {

        "grant_type": "authorization_code",

        "client_id": ML_CLIENT_ID,

        "client_secret": ML_CLIENT_SECRET,

        "code": code,

        "redirect_uri": REDIRECT_URI,

        "code_verifier": pkce["code_verifier"]

    }


    print()
    print("Enviando solicitação...")

    resposta = requests.post(

        TOKEN_URL,

        data=payload,

        headers={
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded"
        }

    )


    print()
    print("Status:", resposta.status_code)
    print(resposta.text)


    if resposta.status_code != 200:

        return


    dados = resposta.json()

    salvar_tokens(dados)

    print()
    print("=" * 70)
    print("TOKEN GERADO COM SUCESSO")
    print("=" * 70)

    print("Access Token:")
    print(dados["access_token"])

    print()
    print("Refresh Token:")
    print(dados["refresh_token"])


# =========================================================
# EXECUTAR TROCA
# =========================================================

print()

codigo = input(
    "Cole aqui o parâmetro CODE recebido na URL:\n\n"
).strip()

trocar_code_por_token(codigo)
