"""
=========================================================
CLIENTE OFICIAL MERCADO LIVRE
=========================================================
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse, parse_qs
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

        print("\n===== RESPOSTA COMPLETA =====")
        print(dados)
        print("=============================\n")
    
        return dados.get("results", [])

    # =====================================================
    # EXTRAI O ID DO ANÚNCIO A PARTIR DA URL
    # =====================================================
    
    def extrair_item_id(self, url):
    
        parsed = urlparse(url)
    
        parametros = parse_qs(parsed.query)
    
        # prioridade para o ID do anúncio (wid)
        if "wid" in parametros:
    
            return parametros["wid"][0]
    
        # depois procura qualquer MLBxxxx existente
        resultado = re.search(r"(MLB\d+)", url.upper())
    
        if resultado:
    
            return resultado.group(1)
    
        raise ValueError(
            f"Não foi possível identificar o Item ID da URL:\n{url}"
        )

    # =====================================================
    # COLETOR PADRÃO
    # =====================================================

    def obter_produto(self, url):

        item_id = self.extrair_item_id(url)

        anuncio = self.obter_anuncio(item_id)

        preco = float(
            anuncio.get("price", 0)
        )

        preco_antigo = anuncio.get("original_price")

        if preco_antigo is None:
            preco_antigo = preco

        preco_antigo = float(preco_antigo)

        if preco_antigo > preco:

            desconto = round(
                ((preco_antigo - preco) / preco_antigo) * 100,
                2
            )

        else:

            desconto = 0.0

        estoque = (
            anuncio.get("available_quantity", 0) > 0
        )

        quantidade = anuncio.get(
            "available_quantity",
            0
        )

        vendidos = anuncio.get(
            "sold_quantity",
            0
        )

        imagem = ""

        if anuncio.get("pictures"):

            imagem = anuncio["pictures"][0].get(
                "secure_url",
                anuncio["pictures"][0].get("url", "")
            )

        categoria = anuncio.get(
            "category_id",
            ""
        )

        marca = ""

        modelo = ""

        atributos = anuncio.get(
            "attributes",
            []
        )

        for atributo in atributos:

            nome = atributo.get(
                "id",
                ""
            ).upper()

            if nome == "BRAND":

                marca = atributo.get(
                    "value_name",
                    ""
                )

            elif nome == "MODEL":

                modelo = atributo.get(
                    "value_name",
                    ""
                )

        return {

            "erro": False,

            "loja": "Mercado Livre",

            "produto": anuncio.get(
                "title",
                ""
            ),

            "preco": preco,

            "preco_antigo": preco_antigo,

            "preco_pix": preco,

            "desconto": desconto,

            "estoque": estoque,

            "quantidade": quantidade,

            "vendidos": vendidos,

            "categoria": categoria,

            "marca": marca,

            "modelo": modelo,

            "imagem": imagem,

            "url": anuncio.get(
                "permalink",
                url
            ),

            "identificador": item_id,

            "mensagem": ""

        }

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
    
