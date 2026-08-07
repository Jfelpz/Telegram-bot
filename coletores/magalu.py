import json
import re

from playwright.sync_api import sync_playwright


class MagaluCollector:
    """
    Coletor oficial Magazine Você / Magazine Luiza.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )

    VIEWPORT = {
        "width": 1366,
        "height": 768
    }

    TIMEOUT = 60000

    HEADLESS = True

    # ==========================================================
    # BAIXA HTML
    # ==========================================================

    def _baixar_html(self, url: str) -> str:

        with sync_playwright() as p:

            browser = None

            try:

                browser = p.chromium.launch(
                    headless=self.HEADLESS
                )

                page = browser.new_page(
                    user_agent=self.USER_AGENT,
                    viewport=self.VIEWPORT
                )

                page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=self.TIMEOUT
                )

                return page.content()

            finally:

                if browser:
                    browser.close()

    # ==========================================================
    # EXTRAI JSON
    # ==========================================================

    def _extrair_json(self, html: str) -> dict:

        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        if not match:
            raise Exception("JSON (__NEXT_DATA__) não encontrado.")

        return json.loads(match.group(1))

    # ==========================================================
    # PRODUTO
    # ==========================================================

    def _produto(self, dados: dict) -> dict:

        try:

            return (
                dados["props"]
                     ["pageProps"]
                     ["data"]
                     ["product"]
            )

        except KeyError as erro:

            raise Exception(
                f"Estrutura inesperada da Magalu: {erro}"
            )

    # ==========================================================
    # MONTA PRODUTO
    # ==========================================================

    def _montar_produto(self, produto: dict) -> dict:

        price = produto.get("price", {})

        installment = produto.get("installment", {})

        rating = produto.get("rating", {})

        seller = produto.get("seller", {})

        brand = produto.get("brand", {})

        category = produto.get("category", {})

        subcategory = produto.get("subcategory", {})

        preco_antigo = float(
            price.get("price") or 0
        )

        preco = float(
            price.get("fullPrice") or preco_antigo
        )

        preco_pix = float(
            price.get("bestPrice") or preco
        )

        if preco_antigo > preco:

            desconto = round(
                ((preco_antigo - preco) / preco_antigo) * 100,
                2
            )

        else:

            desconto = 0

        return {

            "erro": False,

            "loja": "MAGALU",

            "id": produto.get("id"),

            "sku": seller.get("sku"),

            "produto": produto.get("title"),

            "descricao": produto.get("description"),

            "marca": brand.get("label"),

            "categoria": category.get("name"),

            "subcategoria": subcategory.get("name"),

            "preco": preco,

            "preco_antigo": preco_antigo,

            "preco_pix": preco_pix,

            "desconto": desconto,

            "estoque": bool(
                produto.get("available")
            ),

            "imagem": produto.get("image"),

            "url": produto.get("path"),

            "parcelas": installment.get("quantity"),

            "valor_parcela": float(
                installment.get("amount") or 0
            ),

            "avaliacao": rating.get("score"),

            "total_avaliacoes": rating.get("count")

        }

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================

    def coletar(self, url: str) -> dict:

        try:

            html = self._baixar_html(url)

            dados = self._extrair_json(html)

            produto = self._produto(dados)

            return self._montar_produto(produto)

        except Exception as erro:

            return {

                "erro": True,

                "mensagem": str(erro),

                "url": url

            }


# ==========================================================
# WRAPPER
# ==========================================================

def coletar_magalu(url: str):

    coletor = MagaluCollector()

    return coletor.coletar(url)
