import csv
import gzip
import io
import os
import re
from urllib.parse import urlparse

import requests


class AwinFeedCollector:
    """
    Coletor genérico para anunciantes da Awin cujo acesso é via
    Product Feed (CSV), não via API de consulta por produto.

    Cada loja (Kabum, Gigantec, etc.) só precisa herdar essa
    classe informando a variável de ambiente com a URL do feed
    e o nome da loja. O feed é baixado uma única vez por
    execução (cache em memória), e reutilizado para todos os
    produtos consultados na mesma execução.

    A URL colada na planilha (URL_ORIGEM) é comparada com o
    campo 'merchant_deep_link' do feed (a URL "crua" do produto
    no site do lojista, sem rastreamento). Quando encontrada,
    o campo 'aw_deep_link' já é o link de afiliado pronto —
    não é necessário gerar link separadamente.
    """

    # Cache em memória, compartilhado entre instâncias, para
    # não baixar o mesmo feed mais de uma vez por execução.
    _cache_feeds = {}

    def __init__(self, feed_url_env: str, loja_nome: str):

        self.feed_url_env = feed_url_env
        self.loja_nome = loja_nome

    # ==========================================================
    # NORMALIZA URL PARA COMPARAÇÃO
    # ==========================================================

    def _normalizar_url(self, url: str) -> str:

        if not url:
            return ""

        parsed = urlparse(url.strip())

        caminho = parsed.path.rstrip("/")

        # Ignora esquema (http/https), www., query string
        # e barra final — só compara domínio + caminho.
        dominio = parsed.netloc.lower().replace("www.", "")

        return f"{dominio}{caminho}".lower()

    # ==========================================================
    # BAIXA E CARREGA O FEED (com cache)
    # ==========================================================

    def _carregar_feed(self) -> list:

        feed_url = os.getenv(self.feed_url_env)

        if not feed_url:

            raise ValueError(
                f"Variável de ambiente {self.feed_url_env} "
                f"não foi configurada."
            )

        if feed_url in self._cache_feeds:

            print(
                f"[{self.loja_nome}] Usando feed já "
                f"carregado em cache nesta execução."
            )

            return self._cache_feeds[feed_url]

        print(f"[{self.loja_nome}] Baixando feed da Awin...")

        resposta = requests.get(
            feed_url,
            timeout=120
        )

        resposta.raise_for_status()

        print(
            f"[{self.loja_nome}] Download concluído: "
            f"{len(resposta.content)} bytes"
        )

        try:

            conteudo = gzip.decompress(
                resposta.content
            ).decode(
                "utf-8-sig",
                errors="replace"
            )

        except OSError:

            conteudo = resposta.content.decode(
                "utf-8-sig",
                errors="replace"
            )

        leitor = csv.DictReader(
            io.StringIO(conteudo),
            delimiter=";"
        )

        produtos = list(leitor)

        print(
            f"[{self.loja_nome}] Produtos no feed: "
            f"{len(produtos)}"
        )

        self._cache_feeds[feed_url] = produtos

        return produtos

    # ==========================================================
    # CONVERTE VALOR PARA FLOAT
    # ==========================================================

    def _para_float(self, valor) -> float:

        if valor is None or valor == "":
            return 0.0

        texto = str(valor).strip()

        texto = texto.replace("R$", "").strip()

        if "," in texto and "." in texto:
            texto = texto.replace(".", "").replace(",", ".")
        elif "," in texto:
            texto = texto.replace(",", ".")

        texto = re.sub(r"[^\d.]", "", texto)

        try:
            return float(texto)
        except ValueError:
            return 0.0

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================

    def coletar(self, url: str) -> dict:

        try:

            produtos = self._carregar_feed()

            url_alvo = self._normalizar_url(url)

            produto_encontrado = None

            for produto in produtos:

                link_bruto = (
                    produto.get("merchant_deep_link", "")
                )

                if self._normalizar_url(link_bruto) == url_alvo:

                    produto_encontrado = produto
                    break

            if not produto_encontrado:

                return {
                    "erro": True,
                    "mensagem": (
                        f"Produto não encontrado no feed da "
                        f"{self.loja_nome}. Pode ser um produto "
                        f"novo (feed ainda não atualizado) ou "
                        f"a URL não bate com o formato esperado."
                    ),
                    "url": url
                }

            preco = self._para_float(
                produto_encontrado.get("search_price")
            )

            preco_antigo = self._para_float(
                produto_encontrado.get("product_price_old")
                or produto_encontrado.get("rrp_price")
            )

            if preco_antigo <= preco:
                preco_antigo = preco

            desconto = self._para_float(
                produto_encontrado.get("savings_percent")
            )

            if not desconto and preco_antigo > preco > 0:

                desconto = round(
                    ((preco_antigo - preco) / preco_antigo) * 100,
                    2
                )

            em_estoque_texto = str(
                produto_encontrado.get("in_stock", "")
            ).strip().lower()

            estoque = em_estoque_texto in ("1", "true", "yes", "sim")

            link_afiliado = (
                produto_encontrado.get("aw_deep_link")
                or url
            )

            return {

                "erro": False,

                "loja": self.loja_nome,

                "produto": produto_encontrado.get(
                    "product_name", ""
                ),

                "categoria": produto_encontrado.get(
                    "merchant_category", ""
                ),

                "preco": preco,

                "preco_antigo": preco_antigo,

                "preco_pix": preco,

                "desconto": desconto,

                "estoque": estoque,

                "imagem": produto_encontrado.get(
                    "large_image", ""
                ),

                "url": link_afiliado

            }

        except Exception as erro:

            return {

                "erro": True,

                "mensagem": str(erro),

                "url": url

            }
