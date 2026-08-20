import os
import requests


class AwinAPI:

    BASE_URL = "https://api.awin.com"

    def __init__(self):

        self.token = os.getenv("AWIN_TOKEN")

        if not self.token:
            raise ValueError(
                "AWIN_TOKEN não encontrado."
            )

    def headers(self):

        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }

    def get(self, endpoint, params=None):

        url = f"{self.BASE_URL}{endpoint}"

        resposta = requests.get(
            url,
            headers=self.headers(),
            params=params,
            timeout=30
        )

        print(f"Status Awin: {resposta.status_code}")

        resposta.raise_for_status()

        return resposta.json()
