import json
import re
import requests

from bs4 import BeautifulSoup


class AliExpressCollector:

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0 Safari/537.36"
        ),
        "Accept-Language": "pt-BR,pt;q=0.9"
    }

    # =====================================================
    # BAIXA HTML
    # =====================================================

    def _baixar_html(self, url):

        resposta = requests.get(
            url,
            headers=self.HEADERS,
            timeout=30
        )

        resposta.raise_for_status()

        return resposta.text

    # =====================================================
    # JSON-LD
    # =====================================================

    def _extrair_json_ld(self, html):

        soup = BeautifulSoup(html, "html.parser")

        script = soup.find(
            "script",
            type="application/ld+json"
        )

        if not script:

            return None

        try:

            return json.loads(script.string)

        except:

            return None

    # =====================================================
    # NEXT DATA
    # =====================================================

    def _extrair_next_data(self, html):

        match = re.search(

            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',

            html,

            re.S

        )

        if not match:

            return None

        try:

            return json.loads(match.group(1))

        except:

            return None

    # =====================================================
    # PREÇO
    # =====================================================

    def _converter_preco(self, valor):

        if valor is None:

            return 0.0

        try:

            return float(

                str(valor)

                .replace("R$", "")

                .replace(".", "")

                .replace(",", ".")

                .strip()

            )

        except:

            return 0.0

    # =====================================================
    # COLETA
    # =====================================================

    def coletar(self, url):

        html = self._baixar_html(url)

        json_ld = self._extrair_json_ld(html)

        next_data = self._extrair_next_data(html)

        nome = ""

        imagem = ""

        preco = 0

        preco_antigo = 0

        estoque = True

        # =================================================
        # JSON-LD
        # =================================================

        if json_ld:

            nome = json_ld.get("name", "")

            imagem = json_ld.get("image", "")

            offers = json_ld.get("offers", {})

            if isinstance(offers, dict):

                preco = self._converter_preco(

                    offers.get("price")

                )

        # =================================================
        # NEXT DATA
        # =================================================

        if next_data:

            texto = json.dumps(

                next_data,

                ensure_ascii=False

            )

            # preço promocional

            if preco == 0:

                match = re.search(

                    r'"activityAmount"\s*:\s*([0-9.]+)',

                    texto

                )

                if match:

                    preco = float(

                        match.group(1)

                    )

            # preço original

            match = re.search(

                r'"originalPrice"\s*:\s*([0-9.]+)',

                texto

            )

            if match:

                preco_antigo = float(

                    match.group(1)

                )

            # estoque

            if '"availableQuantity":0' in texto:

                estoque = False

        # =================================================
        # DESCONTO
        # =================================================

        desconto = 0

        if preco_antigo > preco > 0:

            desconto = round(

                (

                    (preco_antigo - preco)

                    / preco_antigo

                ) * 100,

                2

            )

        # =================================================
        # RETORNO PADRÃO
        # =================================================

        return {

            "loja": "ALIEXPRESS",

            "produto": nome,

            "categoria": "",

            "preco": preco,

            "preco_antigo": preco_antigo,

            "preco_pix": 0,

            "desconto": desconto,

            "estoque": estoque,

            "imagem": imagem,

            "url": url,

            "erro": False

        }
    # =====================================================
    # WRAPPER
    # =====================================================
    
    def coletar_aliexpress(url):
    
        coletor = AliExpressCollector()
    
        return coletor.coletar(url)
