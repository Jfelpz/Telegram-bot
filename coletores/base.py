"""
=========================================================
COLETOR BASE
Responsável por identificar a loja e chamar o coletor correto.
=========================================================
"""

from urllib.parse import urlparse

from coletores.amazon import coletar_amazon
from coletores.magalu import coletar_magalu
from coletores.aliexpress import coletar_aliexpress
from coletores.mercadolivre import MercadoLivre


# =====================================================
# IDENTIFICA A LOJA
# =====================================================

def identificar_loja(url):

    dominio = urlparse(url).netloc.lower()

    if "amazon" in dominio:
        return "amazon"

    if "magazineluiza" in dominio or "magalu" in dominio:
        return "magalu"

    if "aliexpress" in dominio:
        return "aliexpress"

    if "mercadolivre" in dominio or "mercadolibre" in dominio:
        return "mercadolivre"

    return None


# =====================================================
# COLETOR PRINCIPAL
# =====================================================

def coletar_produto(url):

    loja = identificar_loja(url)

    if loja == "amazon":
        return coletar_amazon(url)

    elif loja == "magalu":
        return coletar_magalu(url)

    elif loja == "aliexpress":
        return coletar_aliexpress(url)

    elif loja == "mercadolivre":

        ml = MercadoLivre()

        return ml.obter_produto(url)

    return {
        "erro": True,
        "mensagem": "Loja não suportada."
    }
