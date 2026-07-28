from playwright.sync_api import sync_playwright

URL = "https://www.magazinevoce.com.br/magazinegrupaodapromocao/smartphone-samsung-a07-128gb-preto-4gb-ram-tela-67-cam-dupla-selfie-8mp/p/240466500/te/ga07/"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    page.goto(URL, wait_until="networkidle")

    html = page.content()

    browser.close()

    palavras = [
        "240015700",
        "240466500",
        "listPrice",
        "bestPrice",
        "offers",
        "videoDetail",
        "video_uuid",
        "graphql",
        "ItemOffer",
        "Smartphone Samsung A07"
    ]

    print("\n")

    for palavra in palavras:

        print(f"{palavra}: {palavra in html}")
