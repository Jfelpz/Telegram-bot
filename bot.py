from datetime import datetime
from zoneinfo import ZoneInfo

from atualizador import atualizar_produtos
from logic import processar

FUSO = ZoneInfo("America/Fortaleza")


def main():

    print("=" * 60)
    print("BOT DE PROMOÇÕES")
    print("=" * 60)

    print(
        datetime.now(FUSO).strftime("%d/%m/%Y %H:%M:%S")
    )

    print()

    # ===========================================
    # ETAPA 1
    # Atualiza todos os produtos
    # ===========================================

    atualizar_produtos()

    print()

    # ===========================================
    # ETAPA 2
    # Procura promoções e publica
    # ===========================================

    processar()

    print()

    print("=" * 60)
    print("BOT FINALIZADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
