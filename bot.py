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

    # =====================================================
    # ETAPA 1
    # Atualiza todos os produtos
    # =====================================================

    houve_repostagem = atualizar_produtos()

    print()

    # =====================================================
    # SE ALGUM PRODUTO ACABOU DE VIRAR PENDENTE,
    # NÃO ENVIA NESTA EXECUÇÃO.
    # =====================================================

    if houve_repostagem:

        print("=" * 60)
        print("REPOSTAGEM LIBERADA")
        print("Os produtos serão enviados na próxima execução.")
        print("=" * 60)

        print()
        print("=" * 60)
        print("BOT FINALIZADO")
        print("=" * 60)

        return

    # =====================================================
    # ETAPA 2
    # Procura promoções pendentes e publica
    # =====================================================

    processar()

    print()

    print("=" * 60)
    print("BOT FINALIZADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
