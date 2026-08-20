from coletores.shopee import ShopeeCollector


print("=" * 50)
print("TESTANDO API DA SHOPEE")
print("=" * 50)

coletor = ShopeeCollector()

url = "COLE_AQUI_UMA_URL_DE_PRODUTO_DA_SHOPEE"

resultado = coletor.coletar(url)

print()

for chave, valor in resultado.items():
    print(f"{chave}: {valor}")
