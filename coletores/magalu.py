from playwright.sync_api import sync_playwright
import re


def coletar_produto(url):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        print(f"Coletando: {url}")

        page.goto(
            url,
            wait_until="networkidle",
            timeout=60000
        )

        html = page.content()

        browser.close()

    dados = {}

    # ==========================
    # TÍTULO
    # ==========================

    titulo = re.search(
        r'"title":"([^"]+)"',
        html
    )

    if titulo:
        dados["produto"] = titulo.group(1)

    # ==========================
    # PREÇO
    # ==========================

    preco = re.search(
        r'"price":([0-9.]+)',
        html
    )

    if preco:
        dados["preco"] = float(preco.group(1))

    # ==========================
    # PREÇO PIX
    # ==========================

    pix = re.search(
        r'"totalAmount":([0-9.]+)',
        html
    )

    if pix:
        dados["preco_pix"] = float(pix.group(1))

    # ==========================
    # ESTOQUE
    # ==========================

    estoque = re.search(
        r'"available":(true|false)',
        html
    )

    if estoque:
        dados["estoque"] = estoque.group(1) == "true"

    return dados
