import json
import re

from playwright.sync_api import sync_playwright


class MagaluCollector:
    """
    Coletor de produtos da Magazine Luiza / Magazine Você.

    Estratégias de extração:
    1. __NEXT_DATA__, caso esteja disponível;
    2. JSON-LD (application/ld+json);
    3. Produto estruturado do tipo schema.org/Product.
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

    TIMEOUT = 90000

    HEADLESS = True

    # ==========================================================
    # CONVERTE VALOR PARA FLOAT
    # ==========================================================

    def _para_float(self, valor) -> float:

        if valor is None:
            return 0.0

        if isinstance(valor, (int, float)):
            return float(valor)

        valor = str(valor).strip()

        valor = valor.replace("R$", "")
        valor = valor.replace("\xa0", "")
        valor = valor.replace(" ", "")

        # Exemplo:
        # 1.299,90 -> 1299.90
        if "," in valor and "." in valor:
            valor = valor.replace(".", "").replace(",", ".")

        elif "," in valor:
            valor = valor.replace(",", ".")

        valor = re.sub(
            r"[^\d.]",
            "",
            valor
        )

        try:
            return float(valor)

        except ValueError:
            return 0.0

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

                print("Abrindo página da Magazine Luiza...")

                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.TIMEOUT
                )

                try:

                    page.wait_for_load_state(
                        "networkidle",
                        timeout=30000
                    )

                except Exception:

                    print(
                        "Aviso: networkidle não foi atingido. "
                        "Continuando com o conteúdo disponível..."
                    )

                page.wait_for_timeout(3000)

                html = page.content()

                print(
                    f"HTML obtido com sucesso. "
                    f"Tamanho: {len(html)} caracteres."
                )

                return html

            finally:

                if browser:
                    browser.close()

    # ==========================================================
    # EXTRAI __NEXT_DATA__
    # ==========================================================

    def _extrair_next_data(self, html: str):

        match = re.search(
            r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
            html,
            re.DOTALL | re.IGNORECASE
        )

        if not match:
            return None

        try:

            return json.loads(
                match.group(1)
            )

        except json.JSONDecodeError:

            return None

    # ==========================================================
    # EXTRAI TODOS OS JSON-LD
    # ==========================================================

    def _extrair_json_ld(self, html: str) -> list:

        scripts = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            re.DOTALL | re.IGNORECASE
        )

        resultados = []

        for script in scripts:

            script = script.strip()

            if not script:
                continue

            try:

                dados = json.loads(script)

                if isinstance(dados, list):

                    resultados.extend(dados)

                else:

                    resultados.append(dados)

            except json.JSONDecodeError:

                continue

        return resultados

    # ==========================================================
    # PROCURA PRODUTO NO JSON-LD
    # ==========================================================

    def _encontrar_produto_json_ld(
        self,
        dados: list
    ) -> dict | None:

        def procurar(obj):

            if isinstance(obj, dict):

                tipo = obj.get("@type")

                if tipo == "Product":
                    return obj

                if isinstance(tipo, list) and "Product" in tipo:
                    return obj

                for valor in obj.values():

                    resultado = procurar(valor)

                    if resultado:
                        return resultado

            elif isinstance(obj, list):

                for item in obj:

                    resultado = procurar(item)

                    if resultado:
                        return resultado

            return None

        for item in dados:

            resultado = procurar(item)

            if resultado:
                return resultado

        return None

    # ==========================================================
    # EXTRAI PRODUTO DO __NEXT_DATA__
    # ==========================================================

    def _produto_next_data(
        self,
        dados: dict
    ) -> dict | None:

        caminhos = [

            [
                "props",
                "pageProps",
                "data",
                "product"
            ],

            [
                "props",
                "pageProps",
                "product"
            ]

        ]

        for caminho in caminhos:

            atual = dados

            try:

                for chave in caminho:
                    atual = atual[chave]

                if isinstance(atual, dict):
                    return atual

            except (
                KeyError,
                TypeError
            ):
                continue

        return None

    # ==========================================================
    # MONTA PRODUTO A PARTIR DO FORMATO ANTIGO
    # ==========================================================

    def _montar_produto_next(
        self,
        produto: dict,
        url_original: str
    ) -> dict:

        price = produto.get("price") or {}

        installment = produto.get("installment") or {}

        rating = produto.get("rating") or {}

        seller = produto.get("seller") or {}

        brand = produto.get("brand") or {}

        category = produto.get("category") or {}

        subcategory = produto.get("subcategory") or {}

        preco_antigo = self._para_float(
            price.get("price")
        )

        preco = self._para_float(
            price.get("fullPrice")
        )

        if preco <= 0:
            preco = preco_antigo

        preco_pix = self._para_float(
            price.get("bestPrice")
        )

        if preco_pix <= 0:
            preco_pix = preco

        if preco_antigo > preco > 0:

            desconto = round(
                (
                    (
                        preco_antigo - preco
                    )
                    / preco_antigo
                )
                * 100,
                2
            )

        else:

            desconto = 0.0

        imagem = produto.get("image") or ""

        if isinstance(imagem, dict):

            imagem = (
                imagem.get("url")
                or imagem.get("src")
                or ""
            )

        url_produto = (
            produto.get("path")
            or url_original
        )

        if (
            url_produto
            and url_produto.startswith("/")
        ):

            url_produto = (
                "https://www.magazineluiza.com.br"
                + url_produto
            )

        return {

            "erro": False,

            "loja": "MAGALU",

            "id": produto.get("id"),

            "sku": seller.get("sku"),

            "produto": (
                produto.get("title")
                or produto.get("name")
                or ""
            ),

            "descricao": (
                produto.get("description")
                or ""
            ),

            "marca": (
                brand.get("label")
                or brand.get("name")
                or ""
            ),

            "categoria": (
                category.get("name")
                or ""
            ),

            "subcategoria": (
                subcategory.get("name")
                or ""
            ),

            "preco": preco,

            "preco_antigo": preco_antigo,

            "preco_pix": preco_pix,

            "desconto": desconto,

            "estoque": bool(
                produto.get("available")
            ),

            "imagem": imagem,

            "url": url_produto,

            "parcelas": installment.get("quantity"),

            "valor_parcela": self._para_float(
                installment.get("amount")
            ),

            "avaliacao": rating.get("score"),

            "total_avaliacoes": rating.get("count")
        }

    # ==========================================================
    # MONTA PRODUTO A PARTIR DO JSON-LD
    # ==========================================================

    def _montar_produto_json_ld(
        self,
        produto: dict,
        url_original: str
    ) -> dict:

        offers = (
            produto.get("offers")
            or {}
        )

        if isinstance(offers, list):

            offers = (
                offers[0]
                if offers
                else {}
            )

        aggregate_rating = (
            produto.get("aggregateRating")
            or {}
        )

        imagem = (
            produto.get("image")
            or ""
        )

        if isinstance(imagem, list):

            imagem = (
                imagem[0]
                if imagem
                else ""
            )

        if isinstance(imagem, dict):

            imagem = (
                imagem.get("url")
                or imagem.get("contentUrl")
                or ""
            )

        preco = self._para_float(
            offers.get("price")
        )

        preco_antigo = self._para_float(
            offers.get("highPrice")
        )

        if preco_antigo <= 0:
            preco_antigo = preco

        preco_pix = preco

        if preco_antigo > preco > 0:

            desconto = round(
                (
                    (
                        preco_antigo - preco
                    )
                    / preco_antigo
                )
                * 100,
                2
            )

        else:

            desconto = 0.0

        disponibilidade = str(
            offers.get("availability")
            or ""
        ).lower()

        estoque = (
            "instock" in disponibilidade
            or "in_stock" in disponibilidade
            or "em estoque" in disponibilidade
        )

        marca = (
            produto.get("brand")
            or ""
        )

        if isinstance(marca, dict):

            marca = (
                marca.get("name")
                or ""
            )

        return {

            "erro": False,

            "loja": "MAGALU",

            "id": (
                produto.get("sku")
                or produto.get("productID")
                or produto.get("mpn")
                or ""
            ),

            "sku": (
                produto.get("sku")
                or ""
            ),

            "produto": (
                produto.get("name")
                or ""
            ),

            "descricao": (
                produto.get("description")
                or ""
            ),

            "marca": marca,

            "categoria": "",

            "subcategoria": "",

            "preco": preco,

            "preco_antigo": preco_antigo,

            "preco_pix": preco_pix,

            "desconto": desconto,

            "estoque": estoque,

            "imagem": imagem,

            "url": (
                produto.get("url")
                or url_original
            ),

            "parcelas": None,

            "valor_parcela": 0.0,

            "avaliacao": (
                aggregate_rating.get(
                    "ratingValue"
                )
            ),

            "total_avaliacoes": (
                aggregate_rating.get(
                    "reviewCount"
                )
            )
        }

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================

    def coletar(
        self,
        url: str
    ) -> dict:

        try:

            print("=" * 50)
            print(
                "INICIANDO COLETA - MAGAZINE LUIZA"
            )
            print("=" * 50)

            print(
                f"URL recebida: {url}"
            )

            html = self._baixar_html(url)

            # ----------------------------------------------
            # TENTATIVA 1: __NEXT_DATA__
            # ----------------------------------------------

            print(
                "Tentando localizar __NEXT_DATA__..."
            )

            dados_next = self._extrair_next_data(
                html
            )

            if dados_next:

                print(
                    "__NEXT_DATA__ encontrado."
                )

                produto = (
                    self._produto_next_data(
                        dados_next
                    )
                )

                if produto:

                    print(
                        "Produto encontrado "
                        "via __NEXT_DATA__."
                    )

                    return (
                        self._montar_produto_next(
                            produto,
                            url
                        )
                    )

                print(
                    "Estrutura de produto "
                    "não encontrada no __NEXT_DATA__."
                )

            else:

                print(
                    "__NEXT_DATA__ não encontrado. "
                    "Tentando JSON-LD..."
                )

            # ----------------------------------------------
            # TENTATIVA 2: JSON-LD
            # ----------------------------------------------

            json_ld = self._extrair_json_ld(
                html
            )

            print(
                f"Blocos JSON-LD encontrados: "
                f"{len(json_ld)}"
            )

            produto_json_ld = (
                self._encontrar_produto_json_ld(
                    json_ld
                )
            )

            if produto_json_ld:

                print(
                    "Produto encontrado via JSON-LD."
                )

                return (
                    self._montar_produto_json_ld(
                        produto_json_ld,
                        url
                    )
                )

            # ----------------------------------------------
            # NENHUMA ESTRATÉGIA FUNCIONOU
            # ----------------------------------------------

            raise Exception(
                "Não foi possível localizar os dados "
                "estruturados do produto. "
                "Nenhum __NEXT_DATA__ ou Product JSON-LD "
                "foi encontrado."
            )

        except Exception as erro:

            print(
                "Erro ao coletar produto da Magazine Luiza:",
                erro
            )

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
