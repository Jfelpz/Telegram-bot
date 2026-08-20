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

    Signature = SHA256(
        AppId + Timestamp + Payload + Secret
    )

    Sem scraping: dados do produto e link de afiliado
    vêm diretamente da API oficial da Shopee.
    """

    # ==========================================================
    # EXTRAI SHOP ID E ITEM ID DA URL DO PRODUTO
    # ==========================================================
    #
    # Formatos suportados:
    #
    # https://shopee.com.br/produto-nome-i.SHOPID.ITEMID
    #
    # https://shopee.com.br/product/SHOPID/ITEMID
    #

    def _extrair_ids(self, url: str):

        resultado = re.search(
            r"i\.(\d+)\.(\d+)",
            url
        )

        if resultado:

            return {
                "shop_id": resultado.group(1),
                "item_id": resultado.group(2)
            }

        resultado = re.search(
            r"/product/(\d+)/(\d+)",
            url
        )

        if resultado:

            return {
                "shop_id": resultado.group(1),
                "item_id": resultado.group(2)
            }

        return None

    # ==========================================================
    # ASSINATURA SHA256
    # ==========================================================

    def _assinar(self, payload_str: str):

        timestamp = str(int(time.time()))

        base = (
            f"{SHOPEE_APP_ID}"
            f"{timestamp}"
            f"{payload_str}"
            f"{SHOPEE_APP_SECRET}"
        )

        assinatura = hashlib.sha256(
            base.encode("utf-8")
        ).hexdigest()

        return timestamp, assinatura

    # ==========================================================
    # CHAMADA GENÉRICA À API GRAPHQL
    # ==========================================================

    def _chamar_api(self, query: str) -> dict:

        payload = {
            "query": query
        }

        payload_str = json.dumps(
            payload,
            separators=(",", ":")
        )

        timestamp, assinatura = self._assinar(
            payload_str
        )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": (
                f"SHA256 "
                f"Credential={SHOPEE_APP_ID}, "
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

        print(
            f"Status Shopee: {resposta.status_code}"
        )

        # Mostra o conteúdo da resposta caso ocorra erro HTTP
        if resposta.status_code >= 400:

            print(
                "Resposta da Shopee:",
                resposta.text
            )

        resposta.raise_for_status()

        dados = resposta.json()

        # Erros retornados pelo GraphQL
        if dados.get("errors"):

            print(
                "Erro GraphQL:",
                dados["errors"]
            )

            raise Exception(
                str(dados["errors"])
            )

        return dados.get("data", {})

    # ==========================================================
    # GERA LINK DE AFILIADO
    # ==========================================================

    def _gerar_link_afiliado(
        self,
        url: str
    ) -> str:

        mutation = f"""
        mutation {{
            generateShortLink(
                input: {{
                    originUrl: {json.dumps(url)}
                    subIds: [
                        "telegram",
                        "bot"
                    ]
                }}
            ) {{
                shortLink
            }}
        }}
        """

        try:

            dados = self._chamar_api(
                mutation
            )

            resultado = dados.get(
                "generateShortLink",
                {}
            )

            link = resultado.get(
                "shortLink"
            )

            if link:

                return link

            print(
                "Aviso: API não retornou shortLink."
            )

            return url

        except Exception as erro:

            print(
                "Aviso: não foi possível "
                "gerar o link de afiliado:",
                erro
            )

            return url

    # ==========================================================
    # BUSCA O PRODUTO
    # ==========================================================

    def _buscar_produto(
        self,
        item_id: str
    ):

        query = f"""
        {{
            productOfferV2(
                itemId: {item_id},
                page: 1,
                limit: 1
            ) {{
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

        dados = self._chamar_api(
            query
        )

        nodes = (
            dados
            .get("productOfferV2", {})
            .get("nodes", [])
        )

        if not nodes:

            return None

        return nodes[0]

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================

    def coletar(
        self,
        url: str
    ) -> dict:

        print("=" * 50)
        print("INICIANDO COLETA - SHOPEE")
        print("=" * 50)

        print(
            f"URL recebida: {url}"
        )

        # ------------------------------------------------------
        # EXTRAI SHOP ID E ITEM ID
        # ------------------------------------------------------

        ids = self._extrair_ids(
            url
        )

        if not ids:

            return {
                "erro": True,

                "mensagem": (
                    "Não foi possível identificar "
                    "o Shop ID e Item ID na URL."
                ),

                "url": url
            }

        shop_id = ids["shop_id"]

        item_id = ids["item_id"]

        print(
            f"Shop ID: {shop_id}"
        )

        print(
            f"Item ID: {item_id}"
        )

        try:

            # --------------------------------------------------
            # BUSCA PRODUTO NA API
            # --------------------------------------------------

            produto = self._buscar_produto(
                item_id
            )

            if not produto:

                return {
                    "erro": True,

                    "mensagem": (
                        "Produto não encontrado "
                        "na API da Shopee."
                    ),

                    "shop_id": shop_id,

                    "item_id": item_id,

                    "url": url
                }

            # --------------------------------------------------
            # PREÇO
            # --------------------------------------------------

            preco = float(
                produto.get(
                    "priceMin"
                ) or 0
            )

            preco_maximo = float(
                produto.get(
                    "priceMax"
                ) or preco
            )

            # --------------------------------------------------
            # DESCONTO
            # --------------------------------------------------

            desconto_valor = float(
                produto.get(
                    "priceDiscountRate"
                ) or 0
            )

            # Algumas APIs retornam:
            #
            # 0.15 = 15%
            #
            # Outras podem retornar:
            #
            # 15 = 15%
            #
            # Então tratamos os dois casos.

            if 0 < desconto_valor <= 1:

                desconto = round(
                    desconto_valor * 100,
                    2
                )

                preco_antigo = round(
                    preco /
                    (1 - desconto_valor),
                    2
                )

            elif desconto_valor > 1:

                desconto = round(
                    desconto_valor,
                    2
                )

                preco_antigo = round(
                    preco /
                    (1 - desconto_valor / 100),
                    2
                )

            else:

                desconto = 0

                preco_antigo = preco

            # --------------------------------------------------
            # GERA LINK DE AFILIADO
            # --------------------------------------------------

            print(
                "Gerando link de afiliado..."
            )

            link_afiliado = (
                self._gerar_link_afiliado(
                    url
                )
            )

            # --------------------------------------------------
            # RESULTADO
            # --------------------------------------------------

            resultado = {

                "erro": False,

                "loja": "SHOPEE",

                "id": produto.get(
                    "itemId",
                    item_id
                ),

                "shop_id": shop_id,

                "produto": produto.get(
                    "productName",
                    ""
                ),

                "categoria": "",

                "preco": preco,

                "preco_maximo": preco_maximo,

                "preco_antigo": preco_antigo,

                "preco_pix": preco,

                "desconto": desconto,

                "estoque": True,

                "imagem": produto.get(
                    "imageUrl",
                    ""
                ),

                "shop": produto.get(
                    "shopName",
                    ""
                ),

                "url_original": url,

                "url": link_afiliado
            }

            print(
                "Produto coletado com sucesso!"
            )

            print(
                f"Produto: {resultado['produto']}"
            )

            print(
                f"Preço: {resultado['preco']}"
            )

            print(
                f"Desconto: {resultado['desconto']}%"
            )

            return resultado

        except Exception as erro:

            print(
                f"Erro ao coletar produto "
                f"da Shopee: {erro}"
            )

            return {

                "erro": True,

                "mensagem": str(erro),

                "shop_id": shop_id,

                "item_id": item_id,

                "url": url
            }
