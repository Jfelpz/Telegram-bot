from aliexpress_api import AliexpressApi, models

from config import (
    ALIEXPRESS_APP_KEY,
    ALIEXPRESS_APP_SECRET,
    ALIEXPRESS_TRACKING_ID
)


class AliExpressCollector:
    """
    Coletor via API oficial de afiliados da AliExpress
    (AliExpress Open Platform / Affiliate API), usando o
    wrapper python-aliexpress-api.

    Diferente do Magalu e do antigo Mercado Livre, aqui não há
    scraping: os dados do produto e o link de afiliado vêm
    diretamente da API oficial, já autorizada pela conta de
    afiliado aprovada.
    """

    def __init__(self):

        self.api = AliexpressApi(
            ALIEXPRESS_APP_KEY,
            ALIEXPRESS_APP_SECRET,
            models.Language.PT,
            models.Currency.BRL,
            ALIEXPRESS_TRACKING_ID
        )

    # ==========================================================
    # GERA O LINK DE AFILIADO PARA A URL DO PRODUTO
    # ==========================================================

    def _gerar_link_afiliado(self, url: str) -> str:

        try:

            links = self.api.get_affiliate_links(url)

            if links:
                return links[0].promotion_link

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

        try:

            produtos = self.api.get_products_details([url])

            if not produtos:

                return {
                    "erro": True,
                    "mensagem": "Produto não encontrado na API.",
                    "url": url
                }

            produto = produtos[0]

            preco = float(
                getattr(produto, "target_sale_price", 0) or 0
            )

            preco_antigo = float(
                getattr(produto, "target_original_price", 0) or preco
            )

            if preco_antigo < preco:
                preco_antigo = preco

            desconto = 0

            if preco_antigo > preco > 0:

                desconto = round(
                    ((preco_antigo - preco) / preco_antigo) * 100,
                    2
                )

            link_afiliado = self._gerar_link_afiliado(url)

            categoria = (
                getattr(produto, "second_level_category_name", "")
                or getattr(produto, "first_level_category_name", "")
            )

            return {

                "erro": False,

                "loja": "ALIEXPRESS",

                "id": getattr(produto, "product_id", ""),

                "produto": getattr(produto, "product_title", ""),

                "categoria": categoria,

                "preco": preco,

                "preco_antigo": preco_antigo,

                "preco_pix": preco,

                "desconto": desconto,

                "estoque": True,

                "imagem": getattr(produto, "product_main_image_url", ""),

                "url": link_afiliado

            }

        except Exception as erro:

            return {

                "erro": True,

                "mensagem": str(erro),

                "url": url

            }
