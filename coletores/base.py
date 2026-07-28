from playwright.sync_api import sync_playwright

URL = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-128gb-preto-4gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466500/te/ga07/"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL, wait_until="networkidle")

    html = page.content()

    browser.close()

    indice = html.find("240466500")

    print(f"Índice: {indice}")

    if indice != -1:

        inicio = max(0, indice - 2500)
        fim = indice + 6000

        print(html[inicio:fim])

    else:
        print("Produto não encontrado.")
