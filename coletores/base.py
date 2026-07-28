from playwright.sync_api import sync_playwright

URL = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-128gb-preto-4gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466500/te/ga07/"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL, wait_until="networkidle")

    scripts = page.locator("script")

    print(f"Total de scripts: {scripts.count()}")

    for i in range(scripts.count()):

        script = scripts.nth(i)

        try:
            script_id = script.get_attribute("id")
            script_type = script.get_attribute("type")

            if script_id or script_type == "application/json":

                print("=" * 80)
                print(f"SCRIPT {i}")
                print("id:", script_id)
                print("type:", script_type)

                texto = script.inner_text()

                print(texto[:5000])

        except Exception:
            pass

    browser.close()
