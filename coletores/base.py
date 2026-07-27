"""
==================================================
BASE DOS COLETORES
==================================================

Responsável por:

- Comunicação com o ScraperAPI
- Tratamento de timeout
- Retry automático
- Retorno do HTML

Todos os coletores utilizam este arquivo.

Exemplo:

from coletores.base import obter_html

html = obter_html(url)
"""

import time
import requests

from config import (
    SCRAPER_API_KEY,
    SCRAPER_TIMEOUT,
    SCRAPER_RETRIES,
    DEBUG
)

# ==================================================
# SESSÃO HTTP
# ==================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    )
})


# ==================================================
# REQUISIÇÃO VIA SCRAPERAPI
# ==================================================

def obter_html(url: str) -> str:
    """
    Faz uma requisição utilizando o ScraperAPI.

    Retorna:
        HTML da página.

    Lança exceção caso todas as tentativas falhem.
    """

    endpoint = "https://api.scraperapi.com/"

    parametros = {
        "api_key": SCRAPER_API_KEY,
        "url": url,
    }

    ultimo_erro = None

    for tentativa in range(1, SCRAPER_RETRIES + 1):

        try:

            if DEBUG:
                print(f"[SCRAPER] Tentativa {tentativa}: {url}")

            resposta = session.get(
                endpoint,
                params=parametros,
                timeout=SCRAPER_TIMEOUT
            )

            resposta.raise_for_status()

            if DEBUG:
                print(
                    f"[SCRAPER] OK ({resposta.status_code})"
                )

            return resposta.text

        except Exception as erro:

            ultimo_erro = erro

            if DEBUG:
                print(
                    f"[SCRAPER] Erro na tentativa {tentativa}: {erro}"
                )

            if tentativa < SCRAPER_RETRIES:
                time.sleep(2)

    raise Exception(
        f"Falha ao consultar o ScraperAPI: {ultimo_erro}"
    )


# ==================================================
# TESTE
# ==================================================

if __name__ == "__main__":

    url = (
        "https://www.magazinevoce.com.br/"
    )

    try:

        html = obter_html(url)

        print("=" * 60)
        print("HTML OBTIDO COM SUCESSO")
        print("=" * 60)

        print(html[:1000])

    except Exception as erro:

        print(f"Erro: {erro}")
