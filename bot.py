from datetime import datetime
from zoneinfo import ZoneInfo

from sheets import carregar_config
from coletor import executar_coletor
from sincronizar import sincronizar_agulha
from logic import processar

FUSO = ZoneInfo("America/Fortaleza")


# =====================================================
# BOT PRINCIPAL
# =====================================================

def main():

    print("=" * 60)
    print("🤖 BOT DE PROMOÇÕES")
    print("=" * 60)

    config = carregar_config()

    # -------------------------------------------------
    # BOT LIGADO?
    # -------------------------------------------------

    if not config.get("BOT_ATIVO", True):

        print("⛔ BOT DESATIVADO NA CONFIG")

        return

    print()

    print(
        f"🕒 Início: {datetime.now(FUSO).strftime('%d/%m/%Y %H:%M:%S')}"
    )

    print()

    # =====================================================
    # 1) PREENCHE A AGULHA
    # =====================================================

    print("=" * 60)
    print("ETAPA 1 - COLETOR")
    print("=" * 60)

    try:

        executar_coletor()

    except Exception as erro:

        print(f"❌ Erro no coletor: {erro}")

    print()

    # =====================================================
    # 2) SINCRONIZA AGULHA -> BANCO_DADOS
    # =====================================================

    print("=" * 60)
    print("ETAPA 2 - SINCRONIZAÇÃO")
    print("=" * 60)

    try:

        sincronizar_agulha()

    except Exception as erro:

        print(f"❌ Erro na sincronização: {erro}")

    print()

    # =====================================================
    # 3) ENVIA PARA TELEGRAM
    # =====================================================

    print("=" * 60)
    print("ETAPA 3 - PUBLICAÇÃO")
    print("=" * 60)

    try:

        processar()

    except Exception as erro:

        print(f"❌ Erro na publicação: {erro}")

    print()

    print("=" * 60)
    print("✅ EXECUÇÃO FINALIZADA")
    print(
        datetime.now(FUSO).strftime("%d/%m/%Y %H:%M:%S")
    )
    print("=" * 60)


# =====================================================
# EXECUÇÃO
# =====================================================

if __name__ == "__main__":

    main()
