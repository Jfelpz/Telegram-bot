from coletores.kabum import ColetorKabum
from coletores.gigantec import ColetorGigantec


print("=" * 50)
print("TESTANDO COLETOR KABUM")
print("=" * 50)

kabum = ColetorKabum()
produtos_kabum = kabum.coletar()

print(produtos_kabum)


print("=" * 50)
print("TESTANDO COLETOR GIGANTEC")
print("=" * 50)

gigantec = ColetorGigantec()
produtos_gigantec = gigantec.coletar()

print(produtos_gigantec)
