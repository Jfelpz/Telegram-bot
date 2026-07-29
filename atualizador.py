from datetime import datetime
from zoneinfo import ZoneInfo

from coletores.base import coletar_produto

from sheets import (
    carregar_banco,
    banco_sheet,
    obter_colunas,
    atualizar_linha
)

FUSO = ZoneInfo("America/Fortaleza")


# =====================================================
# ATUALIZADOR DE PRODUTOS
# =====================================================

def atualizar_produtos():

    print("=" * 60)
    print("ATUALIZANDO PRODUTOS")
    print("=" * 60)

    produtos = carregar_banco()

    colunas = obter_colunas(banco_sheet)

    atualizados = 0
    erros = 0

    for linha, produto in enumerate(produtos, start=2):

        url = str(
            produto.get("URL_ORIGEM", "")
        ).strip()

        if not url:
            continue

        print()
        print(f"[{linha}] Atualizando...")

        print(url)

        try:

            dados = coletar_produto(url)

        except Exception as erro:

            print("Erro:", erro)

            erros += 1

            continue

        if dados.get("erro"):

            print(dados["mensagem"])

            erros += 1

            continue

        atualizar_linha(

            banco_sheet,

            linha,

            {

                colunas["PREÇO"]:
                    dados.get("preco", ""),

                colunas["PREÇO_PIX"]:
                    dados.get("preco_pix", ""),

                colunas["DESCONTO"]:
                    dados.get("desconto", ""),

                colunas["ESTOQUE"]:
                    "EM ESTOQUE"
                    if dados.get("estoque")
                    else "SEM ESTOQUE",

                colunas["MARCA"]:
                    dados.get("marca", ""),

                colunas["CATEGORIA"]:
                    dados.get("categoria", ""),

                colunas["SUBCATEGORIA"]:
                    dados.get("subcategoria", ""),

                colunas["IMAGEM"]:
                    dados.get("imagem", ""),

                colunas["AVALIAÇÃO"]:
                    dados.get("avaliacao", ""),

                colunas["TOTAL_AVALIAÇÕES"]:
                    dados.get("total_avaliacoes", ""),

                colunas["ULTIMA_ATUALIZAÇÃO"]:
                    datetime.now(FUSO).strftime("%d/%m/%Y %H:%M")

            }

        )

        atualizados += 1

        print("✔ Atualizado")

    print()

    print("=" * 60)
    print("FINALIZADO")
    print("=" * 60)

    print(f"Produtos atualizados: {atualizados}")

    print(f"Erros: {erros}")


# =====================================================
# EXECUÇÃO
# =====================================================

if __name__ == "__main__":

    atualizar_produtos()
