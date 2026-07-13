from ranking import gerar_ranking

from sheets import (
    carregar_banco,
    carregar_config,
    escrever_agulha
)


# ==================================================
# MONTA A AGULHA
# ==================================================

def montar_agulha():

    print("=" * 60)
    print("INICIANDO COLETOR")
    print("=" * 60)

    config = carregar_config()

    tamanho_agulha = config.get(
        "TAMANHO_AGULHA",
        36
    )

    banco = carregar_banco()

    print(f"Produtos encontrados: {len(banco)}")

    ranking = gerar_ranking(banco)

    print(f"Produtos elegíveis: {len(ranking)}")

    produtos_agulha = []

    posicao = 1

    for produto in ranking:

        if posicao > tamanho_agulha:
            break

        produtos_agulha.append([

            posicao,

            produto.get("ROW_NUMBER", ""),

            produto.get("ID", ""),

            produto.get("PRODUTO", ""),

            produto.get("URL_ORIGEM", ""),

            produto.get("LINK_AFILIADO", ""),

            "",     # PREÇO (Amapulse)

            "",     # PREÇO ANTIGO

            "",     # DESCONTO

            "",     # ESTOQUE

            ""      # ULTIMA_ATUALIZAÇÃO

        ])

        posicao += 1

    escrever_agulha(produtos_agulha)

    print()

    print(f"{len(produtos_agulha)} produtos enviados para AGULHA.")

    print("Aguardando atualização do Amapulse...")

    print("=" * 60)


# ==================================================
# EXECUÇÃO
# ==================================================

if __name__ == "__main__":

    montar_agulha()
