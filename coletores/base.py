from playwright.sync_api import sync_playwright
import json

URL = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-128gb-preto-4gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466500/te/ga07/"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(URL, wait_until="networkidle")

    dados = page.locator("#__NEXT_DATA__").inner_text()

    browser.close()

    print("Tamanho do JSON:", len(dados))

    palavras = [
        "240466500",
        "bestPrice",
        "listPrice",
        "offers",
        "price",
        "Samsung A07",
        "available"
    ]

    print("\n")

    for palavra in palavras:
        print(f"{palavra}: {palavra in dados}")

    print("\n")

    indice = dados.find("240466500")

    print("Indice:", indice)

    if indice != -1:
        inicio = max(0, indice - 2000)
        fim = indice + 6000

        print(dados[inicio:fim])
