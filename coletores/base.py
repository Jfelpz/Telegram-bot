"""
=========================================================
COLETOR BASE
Responsável por identificar a loja e chamar o coletor correto.
=========================================================
"""

from urllib.parse import urlparse

from coletores.magalu import coletar_magalu
from coletores.aliexpress import coletar_aliexpress
from coletores.mercadolivre import MercadoLivre


# =====================================================
# IDENTIFICA A LOJA
# =====================================================

def identificar_loja(url):

    dominio = urlparse(url).netloc.lower()

    # Magazine Luiza / Magazine Você
    if (
        "magalu" in dominio
        or "magazineluiza" in dominio
        or "magazinevoce" in dominio
    ):
        return "magalu"

    # AliExpress
    if "aliexpress" in dominio:
        return "aliexpress"

    # Mercado Livre
    if (
        "mercadolivre" in dominio
        or "mercadolibre" in dominio
    ):
        return "mercadolivre"

    return None


# =====================================================
# COLETOR PRINCIPAL
# =====================================================

def coletar_produto(url):

    loja = identificar_loja(url)

    print(f"Loja identificada: {loja}")

    if loja == "magalu":
        return coletar_magalu(url)

    elif loja == "aliexpress":
        return coletar_aliexpress(url)

    elif loja == "mercadolivre":

        ml = MercadoLivre()

        return ml.obter_produto(url)

    return {
        "erro": True,
        "mensagem": f"Loja não suportada: {url}"
    }
