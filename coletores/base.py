from playwright.sync_api import sync_playwright
import json

URL = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-128gb-preto-4gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466500/te/ga07/"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    respostas = []

    def capturar(response):
        if "graphql" in response.url.lower():
            try:
                respostas.append({
                    "url": response.url,
                    "status": response.status,
                    "body": response.text()
                })
            except:
                pass

    page.on("response", capturar)

    page.goto(URL, wait_until="networkidle", timeout=60000)

    browser.close()

    print(f"\nEncontradas {len(respostas)} respostas GraphQL\n")

    for i, r in enumerate(respostas):

        print("="*80)
        print(i)
        print(r["url"])
        print("STATUS:", r["status"])
        print(r["body"][:4000])
