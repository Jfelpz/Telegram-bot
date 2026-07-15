from datetime import datetime
from zoneinfo import ZoneInfo

from ranking import gerar_ranking

from sheets import (
    carregar_banco,
    carregar_config,
    escrever_agulha,
    atualizar_celula,
    banco_sheet,
    obter_colunas
)


FUSO = ZoneInfo("America/Fortaleza")


# ==========================================================
# COLETOR PRINCIPAL
# ==========================================================

def executar_coletor():

    print("=" * 60)
    print("INICIANDO COLETOR")
    print("=" * 60)

    # ------------------------------------------------------
    # CONFIG
    # ------------------------------------------------------

    config = carregar_config()

    tamanho_agulha = int(
        config.get(
            "TAMANHO_AGULHA",
            36
        )
    )

    # ------------------------------------------------------
    # PRODUTOS
    # ------------------------------------------------------

    produtos = carregar_banco()

    print(f"Produtos encontrados: {len(produtos)}")

    # ------------------------------------------------------
    # FILTRA APENAS PENDENTES
    # ------------------------------------------------------

    pendentes = []

    for produto in produtos:

        status = str(
            produto.get(
                "STATUS",
                ""
            )
        ).strip().upper()

        ativo = str(
            produto.get(
                "ATIVO",
                ""
            )
        ).strip().upper()

        if status != "PENDENTE":
            continue

        if ativo not in (
            "TRUE",
            "VERDADEIRO",
            "SIM",
            "1"
        ):
            continue

        pendentes.append(produto)

    print(
        f"Produtos pendentes: {len(pendentes)}"
    )

    # ------------------------------------------------------
    # RANKING
    # ------------------------------------------------------

    ranking = gerar_ranking(
        pendentes
    )

    ranking = ranking[:tamanho_agulha]

    print(
        f"Selecionados: {len(ranking)}"
    )

    # ------------------------------------------------------
    # COLUNAS
    # ------------------------------------------------------

    colunas = obter_colunas(
        banco_sheet
    )

    agora = datetime.now(
        FUSO
    ).strftime(
        "%d/%m/%Y %H:%M"
    )

    dados_agulha = []

    # ------------------------------------------------------
    # PREENCHE AGULHA
    # ------------------------------------------------------

    for posicao, produto in enumerate(
        ranking,
        start=1
    ):

        row_banco = produto.get(
            "ROW_NUMBER"
        )

        linha = [

            posicao,

            row_banco,

            produto.get(
                "PRODUTO",
                ""
            ),

            produto.get(
                "ID",
                ""
            ),

            produto.get(
                "URL_ORIGEM",
                ""
            ),

            produto.get(
                "LINK_AFILIADO",
                ""
            ),

            "",     # PREÇO

            "",     # PREÇO ANTIGO

            "",     # DESCONTO

            "",     # ESTOQUE

            agora   # ULTIMA_ATUALIZAÇÃO

        ]

        dados_agulha.append(
            linha
        )

        # ------------------------------------------
        # ALTERA STATUS
        # ------------------------------------------

        atualizar_celula(

            banco_sheet,

            row_banco,

            colunas["STATUS"],

            "NA_AGULHA"

        )

    # ------------------------------------------------------
    # ESCREVE AGULHA
    # ------------------------------------------------------

    escrever_agulha(
        dados_agulha
    )

    print()

    print(
        "AGULHA ATUALIZADA COM SUCESSO."
    )

    print(
        f"{len(dados_agulha)} produto(s) enviados."
    )

    print("=" * 60)


# ==========================================================
# TESTE
# ==========================================================

if __name__ == "__main__":

    executar_coletor()
