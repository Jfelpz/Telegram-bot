import os
import sys
from pprint import pprint

# Adiciona a raiz do projeto ao PATH
ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from coletores.base import coletar_produto


URL = "COLE_AQUI_UMA_URL_DO_ALIEXPRESS"


print("=" * 80)
print("INICIANDO TESTE")
print("=" * 80)

dados = coletar_produto(URL)

print()
print("=" * 80)
print("RESULTADO")
print("=" * 80)

pprint(dados)
