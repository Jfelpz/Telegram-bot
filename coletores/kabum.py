from coletores.awin import AwinAPI


class ColetorKabum:

    def __init__(self):

        self.awin = AwinAPI()

    def coletar(self):

        print("=" * 50)
        print("INICIANDO COLETA - KABUM")
        print("=" * 50)

        try:

            # Aqui colocaremos o endpoint/feed
            # específico da KaBuM na Awin

            print("Coleta da KaBuM iniciada.")

            produtos = []

            return produtos

        except Exception as erro:

            print(
                f"Erro ao coletar produtos da KaBuM: {erro}"
            )

            return []
