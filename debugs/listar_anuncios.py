import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from coletores.mercadolivre import MercadoLivre

print("=" * 60)
print("LISTANDO ANÚNCIOS DO MERCADO LIVRE")
print("=" * 60)

ml = MercadoLivre()

anuncios = ml.listar_anuncios()

print(f"\nTotal de anúncios: {len(anuncios)}\n")

for item in anuncios:
    print(item)
