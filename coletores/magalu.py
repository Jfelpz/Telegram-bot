"""
==================================================
COLETOR MAGALU / MAGAZINE VOCÊ
==================================================

Responsável por:

- Baixar o HTML
- Extrair informações do produto
- Retornar um dicionário padronizado

Todos os coletores do projeto devem seguir
o mesmo formato de retorno.
"""

import json
import re

from bs4 import BeautifulSoup

from coletores.base import obter_html


# ==================================================
# AUXILIAR
# ==================================================

def limpar_preco(valor):

    """
    Converte:

    "R$ 1.299,90"

    para

    1299.90
    """

    if valor is None:
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

    valor = (
        str(valor)
        .replace("R$", "")
        .replace(".", "")
        .replace(",", ".")
        .strip()
    )

    try:
        return float(valor)
    except:
        return None


# ==================================================
# JSON-LD
# ==================================================

def extrair_jsonld(soup):

    scripts = soup.find_all(
        "script",
        type="application/ld+json"
    )

    for script in scripts:

        try:

            conteudo = json.loads(script.string)

            if isinstance(conteudo, list):

                for item in conteudo:

                    if item.get("@type") == "Product":
                        return item

            elif conteudo.get("@type") == "Product":

                return conteudo

        except:

            continue

    return None


# ==================================================
# ESTOQUE
# ==================================================

def estoque_disponivel(texto):

    if texto is None:
        return False

    texto = texto.lower()

    palavras = [
        "instock",
        "in stock",
        "disponível",
        "disponivel"
    ]

    return any(
        palavra in texto
        for palavra in palavras
    )


# ==================================================
# COLETA
# ==================================================

def coletar_produto(url):

    html = obter_html(url)

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    produto = {

        "produto": None,
        "preco": None,
        "preco_antigo": None,
        "estoque": False,
        "url": url,
        "erro": None

    }

    try:

        dados = extrair_jsonld(soup)

        if dados:

            produto["produto"] = dados.get("name")

            offers = dados.get("offers")

            if isinstance(offers, dict):

                produto["preco"] = limpar_preco(
                    offers.get("price")
                )

                disponibilidade = offers.get(
                    "availability",
                    ""
                )

                produto["estoque"] = estoque_disponivel(
                    disponibilidade
                )

            elif isinstance(offers, list):

                offer = offers[0]

                produto["preco"] = limpar_preco(
                    offer.get("price")
                )

                disponibilidade = offer.get(
                    "availability",
                    ""
                )

                produto["estoque"] = estoque_disponivel(
                    disponibilidade
                )

    except Exception as erro:

        produto["erro"] = str(erro)

    return produto


# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    url = "COLE_AQUI_UMA_URL_DA_MAGAZINE_VOCE"

    resultado = coletar_produto(url)

    print()

    print("=" * 60)

    print(resultado)

    print("=" * 60)
