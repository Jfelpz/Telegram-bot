import hashlib
import json
import re
import time

import requests

from config import (
    SHOPEE_APP_ID,
    SHOPEE_APP_SECRET
)

API_URL = "https://open-api.affiliate.shopee.com.br/graphql"


class ShopeeCollector:
    """
    Coletor via API oficial de afiliados da Shopee
    (Open API / Affiliate GraphQL API).

    Autenticação por assinatura SHA256 no header Authorization:
    Signature = SHA256(AppId + Timestamp + Payload + Secret)

    Sem scraping: dados do produto e link de afiliado vêm
    direto da API, usando o App ID/Secret liberados pela Shopee
    após a solicitação de acesso via Central de Ajuda.
    """

    # ==========================================================
    # EXTRAI O ITEM ID DA URL DO PRODUTO
    # ==========================================================
    # URLs da Shopee aparecem em pelo menos dois formatos:
    # https://shopee.com.br/produto-nome-i.SHOPID.ITEMID
    # https://shopee.com.br/product/SHOPID/ITEMID

    def _extrair_item_id(self, url: str) -> str:

        resultado = re.search(r"i\.\d+\.(\d+)", url)

        if resultado:
            return resultado.group(1)

        resultado = re.search(r"/product/\d+/(\d+)", url)

        if resultado:
            return resultado.group(1)

        return ""

    # ==========================================================
    # ASSINATURA SHA256
    # ==========================================================

    def _assinar(self, payload_str: str):

        timestamp = str(int(time.time()))

        base = (
            f"{SHOPEE_APP_ID}{timestamp}{payload_str}{SHOPEE_APP_SECRET}"
        )

        assinatura = hashlib.sha256(
            base.encode("utf-8")
        ).hexdigest()

        return timestamp, assinatura

    # ==========================================================
    # CHAMADA GENÉRICA À API (GraphQL)
    # ==========================================================

    def _chamar_api(self, query: str) -> dict:

        payload_str = json.dumps(
            {"query": query},
            separators=(",", ":")
        )

        timestamp, assinatura = self._assinar(payload_str)

        headers = {
            "Content-Type": "application/json",
            "Authorization": (
                f"SHA256 Credential={SHOPEE_APP_ID}, "
                f"Timestamp={timestamp}, "
                f"Signature={assinatura}"
            )
        }

        resposta = requests.post(
            API_URL,
            data=payload_str,
            headers=headers,
            timeout=30
        )

        resposta.raise_for_status()

        dados = resposta.json()

        if dados.get("errors"):
            raise Exception(str(dados["errors"]))

        return dados.get("data", {})

    # ==========================================================
    # GERA O LINK DE AFILIADO (short link) PARA A URL DO PRODUTO
    # ==========================================================

    def _gerar_link_afiliado(self, url: str) -> str:

        mutation = f"""
        mutation {{
          generateShortLink(
            input: {{
              originUrl: {json.dumps(url)}
              subIds: ["telegram", "bot"]
            }}
          ) {{
            shortLink
          }}
        }}
        """

        try:

            dados = self._chamar_api(mutation)

            return dados["generateShortLink"]["shortLink"]

        except Exception as erro:

            print(
                "Aviso: não foi possível gerar o link de afiliado:",
                erro
            )

            return url

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================

    def coletar(self, url: str) -> dict:

        item_id = self._extrair_item_id(url)

        if not item_id:

            return {
                "erro": True,
                "mensagem": (
                    "Não foi possível identificar o itemId na URL "
                    "(esperado o padrão .../i.SHOPID.ITEMID)."
                ),
                "url": url
            }

        query = f"""
        {{
          productOfferV2(itemId: {item_id}, page: 1, limit: 1) {{
            nodes {{
              itemId
              productName
              imageUrl
              priceMin
              priceMax
              priceDiscountRate
              shopName
            }}
          }}
        }}
        """

        try:

            dados = self._chamar_api(query)

            nodes = (
                dados.get("productOfferV2", {}).get("nodes", [])
            )

            if not nodes:

                return {
                    "erro": True,
                    "mensagem": "Produto não encontrado na API.",
                    "url": url
                }

            produto = nodes[0]

            preco = float(produto.get("priceMin") or 0)

            desconto_fracao = float(
                produto.get("priceDiscountRate") or 0
            )

            desconto = round(desconto_fracao * 100, 2)

            if 0 < desconto_fracao < 1:

                preco_antigo = round(
                    preco / (1 - desconto_fracao),
                    2
                )

            else:

                preco_antigo = preco

            link_afiliado = self._gerar_link_afiliado(url)

            return {

                "erro": False,

                "loja": "SHOPEE",

                "id": produto.get("itemId", item_id),

                "produto": produto.get("productName", ""),

                "categoria": "",

                "preco": preco,

                "preco_antigo": preco_antigo,

                "preco_pix": preco,

                "desconto": desconto,

                "estoque": True,

                "imagem": produto.get("imageUrl", ""),

                "url": link_afiliado

            }

        except Exception as erro:

            return {

                "erro": True,

                "mensagem": str(erro),

                "url": url

            }
