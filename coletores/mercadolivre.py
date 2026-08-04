"""
=========================================================
CLIENTE OFICIAL MERCADO LIVRE
=========================================================
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

import requests

from config import (
    ML_CLIENT_ID,
    ML_CLIENT_SECRET,
)

TOKEN_URL = "https://api.mercadolibre.com/oauth/token"
API_URL = "https://api.mercadolibre.com"

TOKEN_FILE = Path("ml_tokens.json")


class MercadoLivre:

    def __init__(self):

        self.tokens = self.carregar_tokens()

    # =====================================================
    # CARREGAR TOKENS
    # =====================================================

    def carregar_tokens(self):

        if not TOKEN_FILE.exists():

            raise FileNotFoundError(
                "Arquivo ml_tokens.json não encontrado."
            )

        with open(
            TOKEN_FILE,
            "r",
            encoding="utf-8"
        ) as arquivo:

            return json.load(arquivo)

    # =====================================================
    # SALVAR TOKENS
    # =====================================================

    def salvar_tokens(self):

        with open(
            TOKEN_FILE,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                self.tokens,
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    # =====================================================
    # PROPRIEDADES
    # =====================================================

    @property
    def access_token(self):

        return self.tokens["access_token"]

    @property
    def refresh_token(self):

        return self.tokens["refresh_token"]

    @property
    def expires_in(self):

        return int(
            self.tokens.get("expires_in", 21600)
        )

    @property
    def created_at(self):

        valor = self.tokens.get("created_at")

        if not valor:

            return datetime.now()

        return datetime.fromisoformat(valor)

    # =====================================================
    # TEMPO RESTANTE
    # =====================================================

    def tempo_restante(self):

        expiracao = self.created_at + timedelta(
            seconds=self.expires_in
        )

        return expiracao - datetime.now()

    # =====================================================
    # TOKEN EXPIRADO?
    # =====================================================

    def token_expirado(self):

        return self.tempo_restante() <= timedelta(minutes=5)

    # =====================================================
    # RENOVAR TOKEN
    # =====================================================

    def renovar_token(self):

        print("Renovando Access Token...")

        payload = {

            "grant_type": "refresh_token",

            "client_id": ML_CLIENT_ID,

            "client_secret": ML_CLIENT_SECRET,

            "refresh_token": self.refresh_token

        }

        resposta = requests.post(

            TOKEN_URL,

            data=payload,

            timeout=30

        )

        resposta.raise_for_status()

        novos_tokens = resposta.json()

        self.tokens["access_token"] = novos_tokens["access_token"]
        self.tokens["refresh_token"] = novos_tokens["refresh_token"]
        self.tokens["expires_in"] = novos_tokens["expires_in"]
        self.tokens["token_type"] = novos_tokens.get(
            "token_type",
            "Bearer"
        )
        self.tokens["created_at"] = datetime.now().isoformat()

        if "user_id" in novos_tokens:
            self.tokens["user_id"] = novos_tokens["user_id"]

        self.salvar_tokens()

        print("✓ Novo token salvo.")

    # =====================================================
    # GARANTIR TOKEN
    # =====================================================

    def garantir_token(self):

        if self.token_expirado():

            self.renovar_token()

    # =====================================================
    # HEADERS
    # =====================================================

    def headers(self):

        self.garantir_token()

        return {

            "Authorization":
                f"Bearer {self.access_token}",

            "Accept":
                "application/json",

            "Content-Type":
                "application/json"

        }

    # =====================================================
    # GET
    # =====================================================

    def get(self, endpoint, **kwargs):

        url = API_URL + endpoint

        resposta = requests.get(
            url,
            headers=self.headers(),
            timeout=30,
            **kwargs
        )

        if resposta.status_code == 401:

            self.renovar_token()

            resposta = requests.get(
                url,
                headers=self.headers(),
                timeout=30,
                **kwargs
            )

        resposta.raise_for_status()

        return resposta.json()

    # =====================================================
    # POST
    # =====================================================

    def post(self, endpoint, json=None):

        url = API_URL + endpoint

        resposta = requests.post(
            url,
            headers=self.headers(),
            json=json,
            timeout=30
        )

        if resposta.status_code == 401:

            self.renovar_token()

            resposta = requests.post(
                url,
                headers=self.headers(),
                json=json,
                timeout=30
            )

        resposta.raise_for_status()

        return resposta.json()

    # =====================================================
    # PUT
    # =====================================================

    def put(self, endpoint, json=None):

        url = API_URL + endpoint

        resposta = requests.put(
            url,
            headers=self.headers(),
            json=json,
            timeout=30
        )

        if resposta.status_code == 401:

            self.renovar_token()

            resposta = requests.put(
                url,
                headers=self.headers(),
                json=json,
                timeout=30
            )

        resposta.raise_for_status()

        return resposta.json()

    # =====================================================
    # TESTE
    # =====================================================

    def meus_dados(self):

        return self.get("/users/me")
