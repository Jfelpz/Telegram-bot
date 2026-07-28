from coletores.magalu import coletar_magalu

url = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-128gb-preto-4gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466500/te/ga07/"

dados = coletar_magalu(url)

print()

for chave, valor in dados.items():
    print(f"{chave}: {valor}")
