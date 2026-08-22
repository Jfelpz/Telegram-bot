from coletores.magalu import MagaluCollector


print("=" * 50)
print("TESTANDO COLETOR MAGAZINE LUIZA")
print("=" * 50)

coletor = MagaluCollector()

url = (
    "https://www.magazinevoce.com.br/"
    "magazinegrupaodapromocao/"
    "smartphone-samsung-a07-256gb-preto-8gb-ram-"
    "tela-67-cam-dupla-selfie-8mp/"
    "p/240466000/te/ga07/"
)

resultado = coletor.coletar(url)

print()
print("=" * 50)
print("RESULTADO")
print("=" * 50)

for chave, valor in resultado.items():
    print(f"{chave}: {valor}")
