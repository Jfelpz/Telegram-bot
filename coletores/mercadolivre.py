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

# =====================================================
# CAMINHOS
# =====================================================

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TOKEN_FILE = DATA_DIR / "ml_tokens.json"

# =====================================================
# API
# =====================================================

TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

API_URL = "https://api.mercadolibre.com"


class MercadoLivre:

    def __init__(self):

        if not TOKEN_FILE.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado:\n{TOKEN_FILE}"
            )

        self.tokens = self.carregar_tokens()

    # =====================================================
    # CARREGAR TOKENS
    # =====================================================

    def carregar_tokens(self):

        if not TOKEN_FILE.exists():

            raise FileNotFoundError(
                f"Arquivo de tokens não encontrado:\n{TOKEN_FILE}"
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

        print("\n======================================")
        print("RENOVANDO ACCESS TOKEN...")
        print("======================================")

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

        print("\n======================================")
        print("RESPOSTA DA API")
        print("======================================")
        print("Status:", resposta.status_code)
        print(resposta.text)
        print("======================================\n")

        resposta.raise_for_status()

        novos_tokens = resposta.json()

        self.tokens["access_token"] = novos_tokens["access_token"]

        self.tokens["refresh_token"] = novos_tokens["refresh_token"]

        self.tokens["expires_in"] = novos_tokens.get(
            "expires_in",
            21600
        )

        self.tokens["token_type"] = novos_tokens.get(
            "token_type",
            "Bearer"
        )

        self.tokens["created_at"] = datetime.now().isoformat()

        if "user_id" in novos_tokens:

            self.tokens["user_id"] = novos_tokens["user_id"]

        self.salvar_tokens()

        print("======================================")
        print("NOVOS TOKENS SALVOS")
        print("======================================")
        print("Access Token:", self.tokens["access_token"])
        print("Refresh Token:", self.tokens["refresh_token"])
        print("Created At:", self.tokens["created_at"])
        print("======================================")

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

    #=====================================
    #DELETE
    #======================================

    def delete(self, endpoint):

        url = API_URL + endpoint
    
        resposta = requests.delete(
            url,
            headers=self.headers(),
            timeout=30
        )
    
        if resposta.status_code == 401:
    
            self.renovar_token()
    
            resposta = requests.delete(
                url,
                headers=self.headers(),
                timeout=30
            )
    
        resposta.raise_for_status()
    
        if resposta.text:
            return resposta.json()
    
        return {}

    # =====================================================
    # TESTE
    # =====================================================

    def meus_dados(self):

        return self.get("/users/me")

    # =====================================================
    # LISTAR ANÚNCIOS
    # =====================================================
    
    def listar_anuncios(self):
    
        endpoint = f"/users/{self.tokens['user_id']}/items/search"
    
        dados = self.get(endpoint)
    
        return dados.get("results", [])

    # =====================================================
    # OBTER ANÚNCIO
    # =====================================================
    
    def obter_anuncio(self, item_id):
    
        return self.get(f"/items/{item_id}")

    #=======================================================
    # BUSCAR DESCRIÇÃO
    #=======================================================

    def buscar_descricao(self, item_id):

        return self.get(f"/items/{item_id}/description")

    #=======================================================
    # BUSCAR PREÇO
    #=======================================================

    def buscar_preco(self, item_id):
        anuncio = self.obter_anuncio(item_id)
        return anuncio.get("price")

    #=======================================================
    # BUSCAR LINK
    #=======================================================

    def buscar_link(self, item_id):
        anuncio = self.obter_anuncio(item_id)
        return anuncio.get("permalink")

    #=======================================================
    # BUSCAR ESTOQUE
    #=======================================================
    
    def buscar_estoque(self, item_id):
        anuncio = self.obter_anuncio(item_id)
        return anuncio.get("available_quantity")
    
