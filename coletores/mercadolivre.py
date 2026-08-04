"""
=========================================================
CLIENTE OFICIAL MERCADO LIVRE
=========================================================
"""

import json
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
    # ACCESS TOKEN
    # =====================================================

    @property
    def access_token(self):

        return self.tokens["access_token"]

    @property
    def refresh_token(self):

        return self.tokens["refresh_token"]

    # =====================================================
    # RENOVAR TOKEN
    # =====================================================

    def renovar_token(self):

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

        self.tokens = resposta.json()

        self.salvar_tokens()

        print("✓ Token renovado com sucesso.")

    # =====================================================
    # HEADERS
    # =====================================================

    def headers(self):

        return {

            "Authorization":
                f"Bearer {self.access_token}",

            "Content-Type":
                "application/json",

            "Accept":
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
