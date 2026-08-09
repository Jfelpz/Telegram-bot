from urllib.parse import urlparse

from coletores.magalu import MagaluCollector
from coletores.aliexpress import AliExpressCollector
from coletores.mercadolivre import MercadoLivreCollector


class ColetorBase:

    def __init__(self):

        self.coletores = {

            # Magazine Luiza
            "magazinevoce.com.br": MagaluCollector(),
            "magazineluiza.com.br": MagaluCollector(),

            # AliExpress
            "aliexpress.com": AliExpressCollector(),
            "pt.aliexpress.com": AliExpressCollector(),
            "best.aliexpress.com": AliExpressCollector(),
            "m.aliexpress.com": AliExpressCollector(),

            # Mercado Livre
            "mercadolivre.com.br": MercadoLivreCollector(),
            "mercadolibre.com": MercadoLivreCollector(),
        }

    # =====================================================
    # IDENTIFICA A LOJA
    # =====================================================

    def identificar_loja(self, url: str):

        dominio = urlparse(url).netloc.lower()

        dominio = dominio.replace("www.", "")

        # Aceita qualquer subdomínio do AliExpress
        if "aliexpress.com" in dominio:

            return AliExpressCollector()

        for site, coletor in self.coletores.items():

            if site in dominio:

                return coletor

        raise Exception(f"Loja não suportada: {dominio}")

    # =====================================================
    # COLETA
    # =====================================================

    def coletar(self, url: str):

        coletor = self.identificar_loja(url)

        return coletor.coletar(url)


coletor = ColetorBase()


def coletar_produto(url):

    return coletor.coletar(url)
