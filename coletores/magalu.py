import json
import re
from playwright.sync_api import sync_playwright


class MagaluCollector:
    """
    Coletor oficial da Magazine Você / Magazine Luiza.
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

    def _baixar_html(self, url: str) -> str:
        """
        Abre a página utilizando Playwright e retorna o HTML.
        """

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

    def _extrair_json(self, html: str) -> dict:
        """
        Extrai o JSON presente no script __NEXT_DATA__.
        """

        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        if not match:
            raise Exception("JSON (__NEXT_DATA__) não encontrado.")

        return json.loads(match.group(1))

    def _produto(self, dados: dict) -> dict:
        """
        Retorna apenas o objeto product.
        """

        try:
            return (
                dados["props"]
                     ["pageProps"]
                     ["data"]
                     ["product"]
            )

        except KeyError as e:
            raise Exception(f"Estrutura inesperada da Magalu: {e}")

    def _montar_produto(self, produto: dict) -> dict:
        """
        Converte o JSON da Magalu para um formato único do projeto.
        """

        price = produto.get("price", {})
        installment = produto.get("installment", {})
        rating = produto.get("rating", {})
        seller = produto.get("seller", {})
        brand = produto.get("brand", {})
        category = produto.get("category", {})
        subcategory = produto.get("subcategory", {})

        return {

            "loja": "MAGALU",

            "id": produto.get("id"),

            "sku": seller.get("sku"),

            "produto": produto.get("title"),

            "descricao": produto.get("description"),

            "marca": brand.get("label"),

            "categoria": category.get("name"),

            "subcategoria": subcategory.get("name"),

            "preco": float(price.get("price") or 0),

            "preco_pix": float(price.get("bestPrice") or 0),

            "desconto": float(price.get("discount") or 0),

            "estoque": bool(produto.get("available")),

            "imagem": produto.get("image"),

            "link": produto.get("path"),

            "parcelas": installment.get("quantity"),

            "valor_parcela": float(
                installment.get("amount") or 0
            ),

            "avaliacao": rating.get("score"),

            "total_avaliacoes": rating.get("count")
        }

    def coletar(self, url: str) -> dict:
        """
        Método principal do coletor.
        """

        try:

            html = self._baixar_html(url)

            dados = self._extrair_json(html)

            produto = self._produto(dados)

            return self._montar_produto(produto)

        except Exception as e:

            return {
                "erro": True,
                "mensagem": str(e),
                "url": url
            }
