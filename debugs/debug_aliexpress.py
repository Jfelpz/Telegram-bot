from urllib.parse import urlparse

from coletores.magalu import MagaluCollector
from coletores.aliexpress import AliExpressCollector


# =====================================================
# COLETORES
# =====================================================

MAGALU = MagaluCollector()

ALIEXPRESS = AliExpressCollector()


# =====================================================
# IDENTIFICA A LOJA
# =====================================================

def identificar_loja(url):

    dominio = urlparse(url).netloc.lower()

    if (
        "magazineluiza" in dominio
        or "magazinevoce" in dominio
        or "magazinevoce.com.br" in dominio
    ):

        return "MAGALU"

    if "aliexpress.com" in dominio:

        return "ALIEXPRESS"

    if "amazon.com.br" in dominio:

        return "AMAZON"

    if "kabum.com.br" in dominio:

        return "KABUM"

    if "pichau.com.br" in dominio:

        return "PICHAU"

    if "terabyteshop.com.br" in dominio:

        return "TERABYTE"

    return None


# =====================================================
# COLETOR PRINCIPAL
# =====================================================

def coletar_produto(url):

    loja = identificar_loja(url)

    if loja == "MAGALU":

        return MAGALU.coletar(url)

    elif loja == "ALIEXPRESS":

        return ALIEXPRESS.coletar(url)

    elif loja == "AMAZON":

        raise NotImplementedError(
            "Coletor da Amazon ainda não implementado."
        )

    elif loja == "KABUM":

        raise NotImplementedError(
            "Coletor da KaBuM ainda não implementado."
        )

    elif loja == "PICHAU":

        raise NotImplementedError(
            "Coletor da Pichau ainda não implementado."
        )

    elif loja == "TERABYTE":

        raise NotImplementedError(
            "Coletor da Terabyte ainda não implementado."
        )

    raise ValueError(
        f"Loja não suportada: {url}"
    )
