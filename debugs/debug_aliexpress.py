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


URL = "https://pt.aliexpress.com/item/1005011907112742.html?spm=a2g0o.productlist.main.1.4d686906piDYaX&algo_pvid=8b10730b-ee2d-4bdd-bd7b-4115455ad052&algo_exp_id=8b10730b-ee2d-4bdd-bd7b-4115455ad052-0&pdp_ext_f=%7B%22order%22%3A%221394%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21BRL%21169.52%2163.46%21%21%21208.72%2178.14%21%402101c28d17855517650263393e0fbe%2112000056968105427%21sea%21BR%213026984385%21ABX%211%210%21n_tag%3A-29910%3Bd%3A95e69951%3Bm03_new_user%3A-29895%3BpisId%3A5000000210895592&curPageLogUid=vHIC4FrFLmAk&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005011907112742%7C_p_origin_prod%3A"


print("=" * 80)
print("INICIANDO TESTE")
print("=" * 80)

dados = coletar_produto(URL)

print()
print("=" * 80)
print("RESULTADO")
print("=" * 80)

pprint(dados)
