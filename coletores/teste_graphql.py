import json
import requests

ENDPOINT = "https://federation.magazineluiza.com.br/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/138.0 Safari/537.36"
    )
}


def testar(operation_name, query, variables):
    print("=" * 80)
    print(f"OPERAÇÃO: {operation_name}")
    print("=" * 80)

    payload = {
        "operationName": operation_name,
        "query": query,
        "variables": variables
    }

    resposta = requests.post(
        ENDPOINT,
        headers=HEADERS,
        json=payload,
        timeout=30
    )

    print("Status:", resposta.status_code)

    try:
        dados = resposta.json()

        print(json.dumps(
            dados,
            indent=4,
            ensure_ascii=False
        )[:5000])

    except Exception:
        print(resposta.text[:5000])


# ===================================================
# TESTE 1
# ===================================================

query = """
query product($id: String!) {
    product(id: $id) {
        id
        title
    }
}
"""

testar(
    "product",
    query,
    {
        "id": "240015700"
    }
)
