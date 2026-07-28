import json

from playwright.sync_api import sync_playwright


def _extrair_produto(next_data: dict) -> dict:
    """
    Extrai as informações úteis do JSON do Next.js.
    """

    produto = next_data["props"]["pageProps"]["data"]["product"]

    imagem = produto["image"]

    if imagem:
        imagem = (
            imagem
            .replace("{w}", "800")
            .replace("{h}", "800")
        )

    return {

        "loja": "MAGALU",

        "id": produto.get("variationId") or produto.get("id"),

        "sku": produto["seller"].get("sku"),

        "produto": produto["title"],

        "descricao": produto.get("description"),

        "marca": produto["brand"]["label"],

        "categoria": produto["category"]["name"],

        "subcategoria": produto["subcategory"]["name"],

        "preco": float(produto["price"]["price"]),

        "preco_pix": float(produto["price"]["bestPrice"]),

        "desconto": float(produto["price"]["discount"]),

        "estoque": produto["available"],

        "imagem": imagem,

        "link": produto["url"],

        "parcelas": produto["installment"]["quantity"],

        "valor_parcela": float(produto["installment"]["amount"]),

        "avaliacao": produto["rating"]["score"],

        "total_avaliacoes": produto["rating"]["count"]
    }


def coletar_magalu(url: str) -> dict:
    """
    Coleta todas as informações de um produto da Magalu.
    """

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        page.goto(
            url,
            wait_until="networkidle",
            timeout=60000
        )

        next_data = page.locator("#__NEXT_DATA__").inner_text()

        browser.close()

    dados = json.loads(next_data)

    return _extrair_produto(dados)
