from pprint import pprint

from coletores.magalu import MagaluCollector


URL = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-128gb-preto-4gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466500/te/ga07/"


collector = MagaluCollector()

produto = collector.coletar(URL)

pprint(produto)
