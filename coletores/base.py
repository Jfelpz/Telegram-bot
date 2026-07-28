from urllib.parse import urlparse

from coletores.magalu import MagaluCollector


class ColetorBase:

    def __init__(self):

        self.coletores = {
            "magazinevoce.com.br": MagaluCollector(),
            "magazineluiza.com.br": MagaluCollector(),
        }

    def identificar_loja(self, url: str):

        dominio = urlparse(url).netloc.lower()

        dominio = dominio.replace("www.", "")

        for site, coletor in self.coletores.items():

            if site in dominio:
                return coletor

        raise Exception(f"Loja não suportada: {dominio}")

    def coletar(self, url: str):

        coletor = self.identificar_loja(url)

        return coletor.coletar(url)


coletor = ColetorBase()


def coletar_produto(url):

    return coletor.coletar(url)
