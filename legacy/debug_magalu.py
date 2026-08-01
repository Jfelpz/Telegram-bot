import json
from pprint import pprint

from coletores.magalu import MagaluCollector

URL = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-256gb-preto-8gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466000/te/ga07/"

collector = MagaluCollector()

html = collector._baixar_html(URL)

dados = collector._extrair_json(html)

produto = collector._produto(dados)

print("=" * 80)
print("CHAVES DO PRODUTO")
print("=" * 80)

print(produto.keys())

print()

print("=" * 80)
print("OBJETO PRICE")
print("=" * 80)

pprint(produto.get("price"))

print()

print("=" * 80)
print("OBJETO SELLER")
print("=" * 80)

pprint(produto.get("seller"))

print()

print("=" * 80)
print("OBJETO OFFERS")
print("=" * 80)

pprint(produto.get("offers"))

print()

print("=" * 80)
print("OBJETO INSTALLMENT")
print("=" * 80)

pprint(produto.get("installment"))

print()

print("=" * 80)
print("RESULTADO DO COLETOR")
print("=" * 80)

pprint(collector.coletar(URL))
