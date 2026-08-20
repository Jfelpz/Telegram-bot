import os
import json

from coletores.awin import AwinAPI


class ColetorKabum:

    def __init__(self):

        self.awin = AwinAPI()

        self.publisher_id = os.getenv(
            "AWIN_PUBLISHER_ID"
        )

        self.advertiser_id = os.getenv(
            "AWIN_KABUM_ADVERTISER_ID"
        )

        if not self.publisher_id:
            raise ValueError(
                "AWIN_PUBLISHER_ID não encontrado."
            )

        if not self.advertiser_id:
            raise ValueError(
                "AWIN_KABUM_ADVERTISER_ID não encontrado."
            )

    def coletar(self):

        print("=" * 50)
        print("INICIANDO COLETA - KABUM")
        print("=" * 50)

        try:

            endpoint = (
                f"/publishers/{self.publisher_id}"
                f"/awinfeeds/download/"
                f"{self.advertiser_id}-retail-pt_BR.jsonl"
            )

            resposta = self.awin.get_response(
                endpoint
            )

            produtos = []

            for linha in resposta.text.splitlines():

                linha = linha.strip()

                if not linha:
                    continue

                try:

                    produto = json.loads(linha)

                    produtos.append(produto)

                except json.JSONDecodeError:

                    print(
                        "Linha inválida ignorada."
                    )

            print(
                f"Produtos encontrados: "
                f"{len(produtos)}"
            )

            # TESTE:
            # vamos limitar temporariamente
            # para não imprimir milhares de produtos

            return produtos[:5]

        except Exception as erro:

            print(
                f"Erro ao coletar produtos "
                f"da KaBuM: {erro}"
            )

            return []
