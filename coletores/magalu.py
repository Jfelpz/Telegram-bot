import json
import re
from playwright.sync_api import sync_playwright


class MagaluCollector:

    def _baixar_html(self, url: str) -> str:
        """Abre a página usando Playwright e retorna o HTML."""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            page = browser.new_page(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
            )

            page.goto(url, wait_until="networkidle")

            html = page.content()

            browser.close()

            return html

    def _extrair_json(self, html: str) -> dict:
        """Extrai o JSON do __NEXT_DATA__."""

        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.S
        )

        if not match:
            raise Exception("JSON __NEXT_DATA__ não encontrado.")

        return json.loads(match.group(1))
