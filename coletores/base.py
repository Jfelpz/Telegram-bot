from coletores.magalu import coletar_produto

url = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-128gb-preto-4gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466500/te/ga07/"

dados = coletar_produto(url)

print(dados)
