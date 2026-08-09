import json
import re

from playwright.sync_api import sync_playwright


class MercadoLivreCollector:
    """
    Coletor via scraping público do Mercado Livre.

    Não usa a API oficial: o endpoint /items/{id} está bloqueado
    pelo PolicyAgent do Mercado Livre para leitura de itens de
    terceiros (erro access_denied / PA_UNAUTHORIZED_RESULT_FROM_POLICIES),
    mesmo com token válido e mesmo sem token. Testado e confirmado
    que não é bloqueio de IP nem de escopo do app.

    Este coletor lê a mesma página pública que qualquer visitante
    veria no navegador, sem login e sem token.
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
                    wait_until="domcontentloaded",
                    timeout=self.TIMEOUT
                )

                page.wait_for_timeout(3000)

                return page.content()

            finally:

                if browser:
                    browser.close()

    # ==========================================================
    # EXTRAI ID DO ANÚNCIO (só para referência/debug)
    # ==========================================================

    def _extrair_id(self, url: str) -> str:

        resultado = re.search(
            r"wid=(MLB\d+)",
            url,
            re.IGNORECASE
        )

        if resultado:
            return resultado.group(1).upper()

        ids = re.findall(
            r"(MLB\d+)",
            url.upper()
        )

        if ids:

            ids = sorted(
                ids,
                key=lambda x: int(x.replace("MLB", "")),
                reverse=True
            )

            return ids[0]

        return ""

    # ==========================================================
    # JSON-LD (método preferencial — mais estável que classes CSS)
    # ==========================================================

    def _extrair_json_ld(self, html: str) -> dict:

        blocos = re.findall(
            r'<script type="application/ld\+json"[^>]*>(.*?)</script>',
            html,
            re.DOTALL
        )

        for bloco in blocos:

            try:
                dados = json.loads(bloco.strip())
            except Exception:
                continue

            candidatos = dados if isinstance(dados, list) else [dados]

            for candidato in candidatos:

                if not isinstance(candidato, dict):
                    continue

                if candidato.get("@type") == "Product":
                    return candidato

        return {}

    # ==========================================================
    # META TAGS og: (fallback)
    # ==========================================================

    def _extrair_meta(self, html: str, propriedade: str) -> str:

        match = re.search(
            rf'<meta[^>]+property="{propriedade}"[^>]+content="([^"]*)"',
            html,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

        match = re.search(
            rf'<meta[^>]+content="([^"]*)"[^>]+property="{propriedade}"',
            html,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

        return ""

    # ==========================================================
    # PREÇOS VIA CLASSES ANDES (fallback final)
    # ==========================================================

    def _extrair_precos_andes(self, html: str) -> dict:

        preco_antigo = None

        bloco_antigo = re.search(
            r'ui-pdp-price__original-value.*?andes-money-amount__fraction[^>]*>([\d.,]+)',
            html,
            re.DOTALL
        )

        if bloco_antigo:
            preco_antigo = bloco_antigo.group(1)

        preco_atual = None

        bloco_atual = re.search(
            r'ui-pdp-price__second-line.*?andes-money-amount__fraction[^>]*>([\d.,]+)',
            html,
            re.DOTALL
        )

        if bloco_atual:
            preco_atual = bloco_atual.group(1)

        if not preco_atual:

            generico = re.search(
                r'andes-money-amount__fraction[^>]*>([\d.,]+)',
                html
            )

            if generico:
                preco_atual = generico.group(1)

        return {
            "preco_atual": preco_atual,
            "preco_antigo": preco_antigo
        }

    # ==========================================================
    # CONVERTE STRING DE PREÇO -> FLOAT
    # ==========================================================

    def _converter_preco(self, valor) -> float:

        if valor is None:
            return 0.0

        if isinstance(valor, (int, float)):
            return float(valor)

        texto = str(valor).strip()

        texto = texto.replace(".", "").replace(",", ".")

        try:
            return float(texto)
        except ValueError:
            return 0.0

    # ==========================================================
    # ESTOQUE
    # ==========================================================

    def _tem_estoque(self, html: str) -> bool:

        indicadores_sem_estoque = [
            "Produto indisponível",
            "sem estoque",
            "Sem estoque",
            "ui-pdp-message--stock-out"
        ]

        for indicador in indicadores_sem_estoque:
            if indicador in html:
                return False

        return True

    # ==========================================================
    # SALVA HTML DE DEBUG (quando a extração falha)
    # ==========================================================

    def _salvar_debug(self, item_id: str, html: str):

        try:

            from pathlib import Path

            debug_dir = Path(__file__).resolve().parent.parent / "debugs"

            debug_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            caminho = debug_dir / f"ml_{item_id or 'sem_id'}.html"

            caminho.write_text(
                html,
                encoding="utf-8"
            )

            print(f"[DEBUG] HTML salvo em: {caminho}")

        except Exception as erro:
            print("[DEBUG] Não foi possível salvar o HTML:", erro)

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================

    def coletar(self, url: str) -> dict:

        item_id = self._extrair_id(url)

        try:

            html = self._baixar_html(url)

            json_ld = self._extrair_json_ld(html)

            titulo = json_ld.get("name", "")

            imagem = ""

            if json_ld.get("image"):

                img = json_ld["image"]

                imagem = img[0] if isinstance(img, list) else img

            marca = ""

            if isinstance(json_ld.get("brand"), dict):
                marca = json_ld["brand"].get("name", "")

            ofertas = json_ld.get("offers", {})

            preco_json_ld = ofertas.get("price")

            disponibilidade = str(
                ofertas.get("availability", "")
            ).lower()

            if not titulo:
                titulo = self._extrair_meta(html, "og:title")

            if not imagem:
                imagem = self._extrair_meta(html, "og:image")

            precos_andes = self._extrair_precos_andes(html)

            preco = self._converter_preco(
                preco_json_ld or precos_andes["preco_atual"]
            )

            preco_antigo = self._converter_preco(
                precos_andes["preco_antigo"]
            )

            if preco_antigo <= preco:
                preco_antigo = preco

            desconto = 0

            if preco_antigo > preco > 0:

                desconto = round(
                    ((preco_antigo - preco) / preco_antigo) * 100,
                    2
                )

            if disponibilidade:
                estoque = "instock" in disponibilidade
            else:
                estoque = self._tem_estoque(html)

            if not titulo or preco <= 0:

                self._salvar_debug(item_id, html)

                return {
                    "erro": True,
                    "mensagem": (
                        "Não foi possível extrair título/preço via scraping. "
                        "HTML salvo em debugs/ para ajuste dos seletores."
                    ),
                    "url": url
                }

            return {

                "erro": False,

                "loja": "MERCADO_LIVRE",

                "id": item_id,

                "produto": titulo,

                "marca": marca,

                "categoria": "",

                "preco": preco,

                "preco_antigo": preco_antigo,

                "preco_pix": preco,

                "desconto": desconto,

                "estoque": estoque,

                "imagem": imagem,

                "url": url

            }

        except Exception as erro:

            return {

                "erro": True,

                "mensagem": str(erro),

                "url": url

            }
