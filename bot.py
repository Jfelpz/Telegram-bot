from datetime import datetime
from zoneinfo import ZoneInfo

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

    processar()

    print()

    print("=" * 60)
    print("FINALIZADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
