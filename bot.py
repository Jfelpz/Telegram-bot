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

    resultado = atualizar_produtos()

    houve_repostagem = resultado["houve_repostagem"]
    dados_atualizados = resultado["dados_atualizados"]

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
    # PROCURA PROMOÇÕES PENDENTES E PUBLICA
    # =====================================================

    processar(dados_atualizados)

    print()

    print("=" * 60)
    print("BOT FINALIZADO")
    print("=" * 60)


if __name__ == "__main__":
    main()
