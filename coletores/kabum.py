import os
import csv
import gzip
import io
import requests


AWIN_FEED_URL = os.getenv("AWIN_FEED_URL")


def baixar_feed_kabum():
    """
    Baixa e descompacta o feed da Awin.
    """

    if not AWIN_FEED_URL:
        raise ValueError(
            "AWIN_FEED_URL não foi configurada."
        )

    print("=" * 50)
    print("INICIANDO COLETA - KABUM / AWIN")
    print("=" * 50)

    print("Baixando feed da Awin...")

    response = requests.get(
        AWIN_FEED_URL,
        timeout=120
    )

    response.raise_for_status()

    print(
        f"Download concluído: "
        f"{len(response.content)} bytes"
    )

    print("Descompactando feed...")

    try:
        conteudo = gzip.decompress(
            response.content
        ).decode(
            "utf-8-sig",
            errors="replace"
        )

    except OSError:
        print(
            "Aviso: resposta não estava comprimida."
        )

        conteudo = response.content.decode(
            "utf-8-sig",
            errors="replace"
        )

    return conteudo


def ler_produtos_kabum():
    """
    Lê os produtos do CSV da Awin.
    """

    conteudo = baixar_feed_kabum()

    leitor = csv.DictReader(
        io.StringIO(conteudo),
        delimiter=";"
    )

    produtos = []

    for produto in leitor:

        merchant_id = str(
            produto.get(
                "merchant_id",
                ""
            )
        ).strip()

        merchant_name = str(
            produto.get(
                "merchant_name",
                ""
            )
        ).strip()

        # Segurança extra:
        # somente produtos da KaBuM
        if merchant_id != "17729":
            continue

        produtos.append(produto)

    print(
        f"Produtos KaBuM encontrados: "
        f"{len(produtos)}"
    )

    return produtos


if __name__ == "__main__":

    produtos = ler_produtos_kabum()

    print()

    for produto in produtos[:5]:

        print("-" * 50)

        print(
            "Produto:",
            produto.get("product_name")
        )

        print(
            "Preço:",
            produto.get("search_price")
        )

        print(
            "Preço antigo:",
            produto.get("product_price_old")
        )

        print(
            "Desconto:",
            produto.get("savings_percent")
        )

        print(
            "Estoque:",
            produto.get("in_stock")
        )

        print(
            "Status estoque:",
            produto.get("stock_status")
        )

        print(
            "Link afiliado:",
            produto.get("aw_deep_link")
        )

        print(
            "Imagem:",
            produto.get("large_image")
        )
