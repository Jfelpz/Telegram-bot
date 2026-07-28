from playwright.sync_api import sync_playwright

URL = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-128gb-preto-4gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466500/te/ga07/"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL, wait_until="networkidle", timeout=60000)

    scripts = page.locator("script")

    print(f"\nEncontrados {scripts.count()} scripts\n")

    for i in range(scripts.count()):

        texto = scripts.nth(i).inner_text()

        if len(texto) > 200:

            print("=" * 80)
            print(f"SCRIPT {i}")
            print("=" * 80)
            print(texto[:3000])
            print()

    browser.close()
